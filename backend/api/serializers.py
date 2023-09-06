from rest_framework import serializers
from recipes.models import AmountRecipeIngredients, Ingredient, Recipe, Tag
from users.models import Subscription


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['__all__']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ['__all__']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ['__all__']


class AmountRecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор общего количества ингредиентов в рецепте."""

    class Meta:
        model = AmountRecipeIngredients
        fields = '__all__'
        read_only_fields = ['__all__']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['__all__']
