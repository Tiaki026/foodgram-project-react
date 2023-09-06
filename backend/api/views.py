from .serializers import (
    SubscriptionSerializer, TagSerializer,
    RecipeSerializer, AmountRecipeIngredientsSerializer,
    IngredientSerializer
)
from recipes.models import (
    AmountRecipeIngredients, Ingredient, Recipe, Tag, User
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from users.models import Subscription
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
