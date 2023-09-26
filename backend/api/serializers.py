from typing import Any, Dict, List

from django.core.exceptions import ValidationError
from django.db.models import F, QuerySet
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from recipes.models import (AmountRecipeIngredients, Ingredient, Recipe, Tag,
                            User)
from users.models import Subscription


class TagSerializer(ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        # fields = ['id', 'name', 'color', 'slug']
        fields = '__all__'
        read_only_fields = ['__all__']


class IngredientSerializer(ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        # fields = ['id', 'name', 'measurement_unit']
        fields = '__all__'
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
        fields = ['id', 'recipe', 'amount']


class CreateCustomUserSerializer(UserCreateSerializer):
    """Создание пользователя."""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data: dict) -> dict:
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

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверка подписки пользователя."""
        request_user = self.context.get('request').user

        if request_user.is_anonymous or (request_user == obj):
            return False
        return Subscription.objects.filter(
            user=request_user, author=obj
        ).exists()
        # return request_user.subscriber.filter(author=obj).exists()


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

    def validate(self, validated_data: Dict) -> Subscription:
        """Проверка подписки."""
        # author = self.context['request'].user
        user = validated_data['user']
        author = get_object_or_404(User, pk=id)
        if Subscription.objects.filter(
            subscriber=user, author=author
        ).exists():
            raise ValidationError(
                f'Вы уже подписаны на {author}.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            return ValidationError(
                f'{author} не может подписаться на {author}',
                status=status.HTTP_400_BAD_REQUEST
            )
        if not Subscription.objects.filter(
            user=user,
            author=author
        ).exists():
            return ValidationError(
                'Действие невозможно',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Subscription.objects.create(author=author, user=user)

    def get_recipes_count(self, user: User) -> int:
        """Количесвтво рецептов."""
        return user.recipes.count()


class RecipeCreateSerializer(ModelSerializer):
    """Сериализатор создания рецептов."""

    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = AmountRecipeIngredientsSerializer(many=True)

    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = [
            'ingredients', 'tags', 'image', 'author',
            'name', 'text', 'cooking_time'
        ]

    def validate_ingredient(
        self, ingredient_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Валидатор ингредиентов по отдельности."""
        ingredient = get_object_or_404(Ingredient, id=ingredient_item['id'])
        if ingredient.name in self.ingredient_list:
            raise ValidationError(f'{ingredient.name} уже присутствует.')
        self.ingredient_list.append(ingredient.name)
        if int(ingredient_item['amount']) < 1:
            raise ValidationError('Количество не может быть пустым.')
        return ingredient_item

    def validate_ingredients(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидатор ингредиетов."""
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Нельзя приготовить из ничего.')

        self.ingredient_list = []
        for ingredient_item in ingredients:
            self.validate_ingredient(ingredient_item)
        return data

    def validate_tags(self, tags: Tag) -> Tag:
        """Валидатор тегов."""
        if not tags:
            raise ValidationError('Количество не может быть пустым.')
        if len(tags) != len(set(tags)):
            raise ValidationError(f'{tags} уже выбран.')
        return tags

    def ingredients_set(
        self, recipe: Recipe, ingredients: List[Dict[str, Any]]
    ) -> None:
        """Список ингредиентов."""
        amount_recipe_ingredients = []
        for ingredient in ingredients:
            amount_recipe_ingredients.append(
                AmountRecipeIngredients(
                    ingredients=ingredient['ingredient'],
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

    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'author', 'ingredients',
            'tags', 'image', 'text', 'cooking_time',
            'pub_date', 'is_favorited', 'is_in_shopping_cart'
        ]
        # read_only_fields = [
        #     'author', 'is_favorited', 'is_in_shopping_cart', 'tags'
        # ]
        # read_only_fields = ['__all__']

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Находится ли рецепт в избраном."""
        user = self.context.get('view').request.user
        if user.is_authenticated:
            return user.favorited.filter(recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """Находится ли рецепт в списке покупок."""
        user = self.context.get('view').request.user
        if user.is_authenticated:
            return user.shopping.filter(recipe=recipe).exists()
        return False

    def get_ingredients(self, recipe: Recipe) -> QuerySet:
        """Получение ингредиентов."""
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredients_amount__amount')
        )
        return ingredients
