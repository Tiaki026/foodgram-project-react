from django.db.models import Q
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.decorators import action
from .generator import IngredientsFileGenerator
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (
    SubscriptionSerializer, TagSerializer,
    IngredientSerializer, CustomUserSerializer,
    RecipeSerializer, RecipeCreateSerializer, RecipeReadSerializer
)
from .filters import IngredientFilter, RecipeFilter
from .paginator import CustomPagination
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag, User
from users.models import Subscription
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter

    @action(detail=False, methods=['get'])
    def get_ingredients(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # def get_queryset(self):
    #     name = self.request.query_params.get('name')
    #     queryset = self.queryset

    #     if name:
    #         queryset = queryset.filter(name__icontains=name)

    #     return queryset


    # @action(detail=False, methods=['get'])
    # def get_queryset(self):
    #     name = self.request.query_params.get('name')
    #     queryset = self.queryset

    #     if name:
    #         queryset = queryset.filter(name__icontains=name)

    #     return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):

        queryset = self.queryset
        name = self.request.query_params.getlist('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if not self.request.user.is_authenticated:
            return queryset

        is_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_shopping:
            queryset = queryset.filter(in_shopping__user=self.request.user)
        else:
            queryset = queryset.exclude(in_shopping__user=self.request.user)

        is_favorite = self.request.query_params.get('is_favorited')
        if is_favorite:
            queryset = queryset.filter(in_favorited__user=self.request.user)
        else:
            queryset = queryset.exclude(in_favorited__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def download_ingredients(self, request, format):
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

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def add_to_favorited(self, request, pk):
        """Добавление в избранное."""
        recipe = self.get_object()
        request.user.favorited.add(recipe)
        return Response({
            'message': f'Рецепт {recipe.pk} добавлен в избранное.'
        })

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def remove_from_favorited(self, request, pk):
        """Удаление из избранного."""
        recipe = self.get_object()
        request.user.favorited.remove(recipe)
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
            request.user.shopping.recipes.add(*recipes)
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
            request.user.shopping.recipes.remove(*recipes)
            return Response({'message': 'Рецепт удален из списка покупок.'})
        else:
            return Response({'message': 'Пусто.'})


class UserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = [DjangoModelPermissions]
    pagination_class = CustomPagination

    @action(
        detail=True, methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписаться."""
        user = self.get_object()
        if user != request.user:
            Subscription.objects.get_or_create(author=user, user=request.user)
            return Response(
                {'detail': 'Вы подписаны!'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True, methods=['delete'], permission_classes=[IsAuthenticated]
    )
    def unsubscribe(self, request, pk=None):
        """Отписаться."""
        user = self.get_object()
        if user != request.user:
            Subscription.objects.filter(
                author=user, user=request.user
            ).delete()
            return Response(
                {'detail': 'Вы отписались от пользователя.'},
                status=status.HTTP_200_OK
            )
        return Response(
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscription(self, request):
        """Подписка."""
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
