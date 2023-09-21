from rest_framework.serializers import ModelSerializer, ValidationError
from recipes.models import (
    AmountRecipeIngredients, Ingredient, Recipe, Tag, User
)
from users.models import Subscription
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework import status


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ["__all__"]


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ["__all__"]


class RecipeSerializer(ModelSerializer):
    """Сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image',
            'cooking_time'
        ]
    read_only_fields = ["__all__"]


class AmountRecipeIngredientsSerializer(ModelSerializer):
    """Сериализатор количества ингредиентов."""

    id = IntegerField(write_only=True)

    class Meta:
        model = AmountRecipeIngredients
        fields = ['id', 'amount']


class CreateCustomUserSerializer(UserCreateSerializer):
    """Создание пользователя."""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    # def validate(self, data):
    #     """Проверка регистрации пользователя."""
    #     if data['username'] == 'me':
    #         raise ValidationError(
    #             'Это имя уже занято'
    #         )
    #     if data['email'] == data['username']:
    #         raise ValidationError(
    #             'Поля не должны совпадать'
    #         )
    #     return data


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = SerializerMethodField()

    class Meta():
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj: User):
        """Проверка подписки пользователя."""
        user = self.context.get('request').user

        if user.is_authenticated or user == obj:
            return user.subscribing.filter(author=obj).exists()
        return False


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipe = RecipeSerializer(read_only=True, many=True)
    # recipe = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count'
        ]
        read_only_fields = ['__all__']

    def validate(self, validated_data):
        """Проверка подписки."""
        author = self.context['request'].user
        user = validated_data['user']
        if Subscription.objects.filter(
            subscriber=user, author=author
        ).exists():
            raise ValidationError(
                'Вы уже подписаны на этого автора.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                'Нельзя подписываться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )

        return Subscription.objects.create(author=author, user=user)

    # def get_recipes(self, obj):
    #     request = self.context.get('request')
    #     limit = request.GET.get('recipes_limit')
    #     recipes = obj.recipes.all()
    #     if limit:
    #         recipes = recipes[:int(limit)]
    #     serializer = RecipeSerializer(recipes, many=True, read_only=True)
    #     return serializer.data

    def get_recipes_count(self, obj: User):
        """Количесвтво рецептов."""
        return obj.recipe.count()


class RecipeCreateSerializer(ModelSerializer):
    """Сериализатор создания рецептов."""

    author = CustomUserSerializer(read_only=True)
    # ingredients = PrimaryKeyRelatedField(
    #     many=True, queryset=Ingredient.objects.all(),
    #     required=True, write_only=True
    # )
    # ingredients = AmountRecipeIngredientsSerializer(many=True)
    ingredients = SerializerMethodField()
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'author', 'ingredients',
            'tags', 'image', 'text', 'cooking_time',
            'pub_date',
        ]

    def get_ingredients(self, recipe: Recipe):
        """Получение ингредиентов."""
        return recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredients_amount__amount')
        )

    def ingredients_set(self, recipe, ingredients):
        """Список ингредиентов."""
        # AmountRecipeIngredients.objects.bulk_create(
        #     [AmountRecipeIngredients(
        #         ingredient=Ingredient.objects.get(id=ingredient['id']),
        #         recipe=recipe,
        #         amount=ingredients['amount']
        #     ) for ingredient in ingredients]
        # )
        amount_ingredients = []

        for ingredient, amount in ingredients:
            amount_ingredients.append(
                AmountRecipeIngredients(
                    recipe=recipe, ingredients=ingredient, amount=amount
                )
            )

        AmountRecipeIngredients.objects.bulk_create(amount_ingredients)

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)
        self.ingredients_set(recipe, ingredients)

        return recipe

    def update(self, recipe: Recipe, validated_data: dict):
        """Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            self.ingredients_set(recipe, ingredients)

        recipe.save()
        return recipe


class RecipeReadSerializer(ModelSerializer):
    """Сериализатор чтения рецептов."""

    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

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

    def get_is_favorited(self, recipe: Recipe):
        """Находится ли рецепт в избраном."""
        user = self.context.get('view').request.user
        if user.is_authenticated:
            return user.favorited.filter(recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe: Recipe):
        """Находится ли рецепт в списке покупок."""
        user = self.context.get('view').request.user
        if user.is_authenticated:
            return user.shopping.filter(recipe=recipe).exists()
        return False

    def get_ingredients(self, recipe: Recipe):
        """Получение ингредиентов."""
        return recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredients_amount__amount')
        )
