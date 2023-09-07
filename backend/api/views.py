

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .generator import IngredientsFileGenerator
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (
    SubscriptionSerializer, TagSerializer,
    RecipeSerializer, AmountRecipeIngredientsSerializer,
    IngredientSerializer, UserSerializer
)
from recipes.models import (
    AmountRecipeIngredients, Ingredient, Recipe, Tag, User
)
from users.models import Subscription
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response


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

    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def download_ingredients(request, format):
        """Скачивание файла с ингредиентами в нескольких форматах."""
        ingredients = Ingredient.objects.all()
        ingredient_cart = [ingredient.name for ingredient in ingredients]

        file_generator = IngredientsFileGenerator(ingredient_cart)

        if format == 'pdf':
            return file_generator.generate_pdf()
        elif format == 'doc':
            return file_generator.generate_doc()
        elif format == 'txt':
            return file_generator.generate_txt()

        return HttpResponse('Неверный формат.')

    @action(detail=False, methods=['get'])
    def ingredient_search(self, request):
        """Поиск ингредиентов."""
        query = request.GET.get('q')
        if query:
            ingredients = Ingredient.objects.filter(Q(name__icontains=query))
        else:
            ingredients = Ingredient.objects.all()

        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def add_to_favorite(self, request, pk=None):
        """Добавление в избранное."""
        recipe = self.get_object()
        request.user.favorite.add(recipe)
        return Response({
            'message': f'Рецепт {recipe.pk} добавлен в избранное.'
        })

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def remove_from_favorite(self, request, pk=None):
        """Удаление из избранного."""
        recipe = self.get_object()
        request.user.favorite.remove(recipe)
        return Response({
            'message': f'Рецепт {recipe.pk} удалён из избранного.'
        })

    @action(
        detail=False, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def add_to_shopping_cart(self, request):
        """Добавление в список покупок."""
        recipe_ids = request.data.get('recipe_ids')
        if recipe_ids:
            recipes = Recipe.objects.filter(id__in=recipe_ids)
            request.user.shopping_cart.recipes.add(*recipes)
            return Response({'message': 'Рецепт добавлен в список покупок.'})
        else:
            return Response({'message': 'Пусто.'})

    @action(
        detail=False, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def remove_from_shopping_cart(self, request):
        """Удаление из списка покупок."""
        recipe_ids = request.data.get('recipe_ids')
        if recipe_ids:
            recipes = Recipe.objects.filter(id__in=recipe_ids)
            request.user.shopping_cart.recipes.remove(*recipes)
            return Response({'message': 'Рецепт удален из списка покупок.'})
        else:
            return Response({'message': 'Пусто.'})


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
