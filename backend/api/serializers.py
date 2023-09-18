from rest_framework import serializers
from recipes.models import (
    AmountRecipeIngredients, Ingredient, Recipe, Tag, User
)
from users.models import Subscription
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField


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
        read_only_fields = ['id', 'name', 'measurement_unit']


class CreateCustomUserSerializer(UserCreateSerializer):
    """Создание пользователя."""

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name',
            'last_name', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """Проверка регистрации пользователя."""
        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Это имя уже занято'
            )
        if data['email'] == data['username']:
            raise serializers.ValidationError(
                'Поля не должны совпадать'
            )
        return data


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.subscribing.all()
        return False


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipe = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'
        extra_fields = ['recipes', 'recipes_count']
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
        return obj.recipe.count()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image',
            'cooking_time'
        ]


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all(),
        required=True, write_only=True
    )
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
        required=True, write_only=True
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'author', 'ingredients',
            'tags', 'image', 'text', 'cooking_time',
            'pub_date',
        ]

    def get_ingredients(self, obj):
        """Получение ингредиентов."""
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredients_amount__amount')
        )

    def ingredients_set(self, recipe, ingredients):
        """Список ингредиентов."""
        AmountRecipeIngredients.objects.filter(recipe=recipe).delete()
        amount_ingredients = [
            AmountRecipeIngredients(
                recipe=recipe, ingredients=ingredient, amount=amount
            )
            for ingredient, amount in ingredients
        ]
        AmountRecipeIngredients.objects.bulk_create(amount_ingredients)

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)
        self.ingredients_set(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        if tags is not None:
            instance.tags.clear()
            instance.tags.set(tags)

        self.ingredients_set(instance, ingredients)
        instance.save()

        return instance


    # def get_ingredients(self, obj):
    #     """Получение ингредиентов."""
    #     return obj.ingredients.values(
    #         'id', 'name', 'measurement_unit',
    #         amount=F('ingredients_amount__amount')
    #     )

    # def ingredients_set(recipe, ingredients):
    #     """Список ингредиентов."""
    #     amount_ingredients = []
    #     for ingredient, amount in ingredients.values():
    #         amount_ingredients.append(
    #             AmountRecipeIngredients(
    #                 recipe=recipe, ingredients=ingredient, amount=amount
    #             )
    #         )

    #     AmountRecipeIngredients.objects.bulk_create(amount_ingredients)

    # def create(self, validated_data):
    #     """Создание рецепта."""
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')
    #     recipe = Recipe.objects.create(**validated_data)

    #     recipe.tags.set(tags)
    #     self.ingredients_set(recipe, ingredients)

    #     return recipe

    # def update(self, instance, validated_data):
    #     """Обновление рецепта."""
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')

    #     instance.name = validated_data.get('name', instance.name)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.cooking_time = validated_data.get(
    #         'cooking_time', instance.cooking_time
    #     )
    #     instance.image = validated_data.get('image', instance.image)

    #     instance.tags.clear()
    #     instance.tags.set(tags)
    #     instance.ingredients.clear()
    #     self.ingredients_set(instance, ingredients)
    #     instance.save()

    #     return instance


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'author', 'ingredients',
            'tags', 'image', 'text', 'cooking_time',
            'pub_date', 'is_favorited', 'is_in_shopping_cart'
        ]
        read_only_fields = [
            'author', 'is_favorited', 'is_in_shopping_cart'
        ]

    def get_is_favorited(self, obj):
        """Находится ли рецепт в избраном."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.in_favorited(user)
        return False

    def get_is_in_shopping_cart(self, obj):
        """Находится ли рецепт в списке покупок."""
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.in_shopping(user)
        return False

    def get_ingredients(self, obj):
        """Получение ингредиентов."""
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredients_amount__amount')
        )