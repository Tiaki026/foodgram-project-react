from rest_framework.serializers import ModelSerializer
from recipes.models import (
    AmountRecipeIngredients, Ingredient, Recipe, Tag, User
)
from rest_framework.fields import IntegerField, SerializerMethodField
from users.models import Subscription
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework import status
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.relations import PrimaryKeyRelatedField
from django.db.transaction import atomic
from typing import Dict, Any, List


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['__all__']


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['__all__']


class RecipeSerializer(ModelSerializer):
    """Сериализатор рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image',
            'cooking_time'
        ]
    read_only_fields = ['__all__']


class AmountRecipeIngredientsSerializer(ModelSerializer):
    """Сериализатор количества ингредиентов."""

    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    recipe = PrimaryKeyRelatedField(read_only=True)
    amount = IntegerField(write_only=True)

    class Meta:
        model = AmountRecipeIngredients
        fields = ['recipe', 'id', 'amount']


class CreateCustomUserSerializer(UserCreateSerializer):
    """Создание пользователя."""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """Проверка регистрации пользователя."""
        if data['username'] == 'me':
            raise ValidationError(
                'Это имя уже занято'
            )
        if data['email'] == data['username']:
            raise ValidationError(
                'Поля не должны совпадать'
            )
        return data


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

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователя."""
        request = self.context.get('request')

        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipes = RecipeSerializer(read_only=True, many=True)
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

    def get_recipes_count(self, user: User):
        """Количесвтво рецептов."""
        return user.recipe.count()


class RecipeCreateSerializer(ModelSerializer):
    """Сериализатор создания рецептов."""

    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = AmountRecipeIngredientsSerializer(many=True)

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image', 'author',
            'name', 'text', 'cooking_time'
        ]

    def validate_ingredient(self, ingredient_item: Dict[str, Any]) -> Dict[str, Any]:
        ingredient = get_object_or_404(Ingredient, id=ingredient_item['id'])
        if ingredient.name in self.ingredient_list:
            raise ValidationError(f'{ingredient.name} уже присутствует.')
        self.ingredient_list.append(ingredient.name)
        if int(ingredient_item['amount']) < 1:
            raise ValidationError('Количество не может быть пустым.')
        return ingredient_item

    def validate_ingredients(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Нельзя приготовить из ничего.')

        self.ingredient_list = []
        for ingredient_item in ingredients:
            self.validate_ingredient(ingredient_item)
        return data

    def validate_tags(self, tags: Tag) -> Tag:
        if not tags:
            raise ValidationError('Количество не может быть пустым.')
        if len(tags) != len(set(tags)):
            raise ValidationError(f'{tags} уже выбран.')
        return tags

    def ingredients_set(self, recipe: Recipe, ingredients: List[Dict[str, Any]]) -> None:
        """Список ингредиентов."""
        amount_recipe_ingredients = []
        for ingredient in ingredients:
            amount_recipe_ingredients.append(
                AmountRecipeIngredients(
                    # ingredients=ingredient['ingredient'],
                    Ingredient.objects.get(id=ingredient['id']),
                    recipe=recipe,
                    amount=ingredient['amount']
                )
            )
        AmountRecipeIngredients.objects.bulk_create(amount_recipe_ingredients)

    @atomic
    def create(self, validated_data: dict) -> Recipe:
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)
        self.ingredients_set(recipe, ingredients)

        return recipe

    @atomic
    def update(self, recipe: Recipe, validated_data: dict) -> Recipe:
        """Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        update_fields = []

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)
                update_fields.append(key)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            self.ingredients_set(recipe=recipe, ingredients=ingredients)

        recipe.save(update_fields=update_fields)
        return recipe

    def to_representation(self, instance: Recipe) -> dict:
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class RecipeReadSerializer(ModelSerializer):
    """Сериализатор чтения рецептов."""

    author = CustomUserSerializer()
    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True)
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
            'author', 'is_favorited', 'is_in_shopping_cart', 'tags'
        ]

    def get_is_favorited(self, recipe: Recipe):
        """Находится ли рецепт в избраном."""
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.favorited.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe: Recipe):
        """Находится ли рецепт в списке покупок."""
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.shopping.filter(recipe=recipe).exists()

    def get_ingredients(self, recipe: Recipe):
        """Получение ингредиентов."""
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredients_amount__amount')
        )
        return ingredients
