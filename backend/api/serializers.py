from rest_framework import serializers
from recipes.models import (
    AmountRecipeIngredients, Ingredient, Recipe, Tag, User
)
from users.models import Subscription
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from djoser.serializers import UserSerializer, UserCreateSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id']


class CreateCustomUserSerializer(UserCreateSerializer):
    """Создание пользователя."""

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name',
            'last_name', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = '__all__'
        extra_fields = ['is_subscribed']
        read_only_fields = ['id', 'is_subscribed']

    # def create(self, validated_data):
    #     """Создание пользователя."""
    #     user = User.objects.create_user(
    #         username=validated_data['username'],
    #         email=validated_data['email'],
    #         password=validated_data['password'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name']
    #     )
    #     return user

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.subscribed.all()
        return False


# class AmountRecipeIngredientsSerializer(serializers.ModelSerializer):
#     """Сериализатор общего количества ингредиентов в рецепте."""

#     recipe = serializers.PrimaryKeyRelatedField(read_only=True)
#     ingredients = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = AmountRecipeIngredients
#         fields = ['id', 'amount']
#         read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    favorite = serializers.SerializerMethodField()
    shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'author', 'ingredients',
            'tags', 'image', 'text', 'cooking_time',
            'pub_date', 'favorite', 'shopping_cart'
        ]
        read_only_fields = ['id', 'author', 'is_favorite', 'is_shopping_cart']

    def create(self, validated_data):
        """Создание рецепта."""
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        amount_data = validated_data.pop('amount')

        recipe = Recipe.objects.create(**validated_data)

        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            recipe.tags.add(tag)

        for ingredient_data in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(**ingredient_data)
            recipe.ingredients.add(ingredient)

        AmountRecipeIngredients.objects.create(
            recipe=recipe,
            ingredients=ingredient,
            amount=amount_data
        )

        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        instance.tags.clear()
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            instance.tags.add(tag)

        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient, _ = Ingredient.objects.get_or_create(**ingredient_data)
            instance.ingredients.add(ingredient)

        instance.save()

        return instance

    def get_favorite(self, obj):
        """Находится ли рецепт в избраном."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.is_favorite(user)
        return False

    def get_shopping_cart(self, obj):
        """Находится ли рецепт в списке покупок."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.is_shopping_cart(user)
        return False

    def get_ingredients(self, obj):
        """Список ингредиентов."""
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('amountrecipeingredients__amount')
        )
        return ingredients


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipe = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        extra_fields = ['recipes', 'recipes_count', 'is_subscribed']
        read_only_fields = ['username', 'email']

    def create(self, validated_data):
        """Создание подписки."""
        author = self.context['request'].user
        user = validated_data['user']
        if Subscription.objects.filter(
            subscriber=user, author=author
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )

        return Subscription.objects.create(author=author, user=user)

    def get_recipes_count(self, obj):
        """Количесвтво рецептов."""
        return Recipe.objects.filter(user=obj).count()
