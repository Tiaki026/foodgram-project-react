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
from .mixins import AddOrDeleteMixin
from .filters import IngredientFilter, RecipeFilter
from .paginator import CustomPagination
from djoser.views import UserViewSet
from recipes.models import (
    Ingredient, Recipe, Favorite, Tag,
    ShoppingCart, AmountRecipeIngredients, User
)
from users.models import Subscription
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum


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
    filterset_class = IngredientFilter

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')

        if name:
            return queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet, AddOrDeleteMixin):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.select_related('author')
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    # def get_queryset(self):
    #     queryset = self.queryset
    #     name = self.request.query_params.getlist('name')
    #     if name:
    #         queryset = queryset.filter(name__icontains=name)
    #     tags = self.request.query_params.getlist('tags')
    #     if tags:
    #         queryset = queryset.filter(tags__slug__in=tags).distinct()

    #     author = self.request.query_params.get('author')
    #     if author:
    #         queryset = queryset.filter(author=author)

    #     if not self.request.user.is_authenticated:
    #         return queryset

    #     is_shopping = self.request.query_params.get('is_in_shopping_cart')
    #     if is_shopping:
    #         queryset = queryset.filter(in_shopping__user=self.request.user)
    #     else:
    #         queryset = queryset.exclude(in_shopping__user=self.request.user)

    #     is_favorite = self.request.query_params.get('is_favorited')
    #     if is_favorite:
    #         queryset = queryset.filter(in_favorited__user=self.request.user)
    #     else:
    #         queryset = queryset.exclude(in_favorited__user=self.request.user)

    #     return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request, format, user):
        """Скачивание файла с ингредиентами в нескольких форматах."""
        shopping_cart = [
            f'Список покупок для {user.username}'
        ]
        if not user.shopping.exists():
            return Response(
                f'Это для {user.username}',
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = (
            AmountRecipeIngredients.objects.filter(
                recipe__ingredients_amount__in_shopping__user=user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(amount=Sum('amount'))
        )
        ingredient_cart = (
            f"{i['ingredient__name']}: {i['amount']}"
            f"{i['ingredient__measurement_unit']}"
            for i in ingredients
        )
        shopping_cart.extend(ingredient_cart)
        file_generator = IngredientsFileGenerator(shopping_cart)

        if format == 'pdf':
            return file_generator.generate_pdf()
        elif format == 'doc':
            return file_generator.generate_doc()
        elif format == 'txt':
            return file_generator.generate_txt()

        return shopping_cart

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добавление и удаление из избранного."""
        if request.method == 'POST':
            return self._add_connection(Favorite, request.user, pk)
        else:
            return self._delete_connection(Favorite, request.user, pk)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавление и удаление из списка покупок."""
        if request.method == 'POST':
            return self._add_connection(ShoppingCart, request.user, pk)
        else:
            return self._delete_connection(ShoppingCart, request.user, pk)


class UserViewSet(UserViewSet, AddOrDeleteMixin):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        """Добавление и удаление подписки."""
        # user = request.user
        # author_id = kwargs.get('id')
        # author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            return self._add_connection(Subscription, request.user, pk)
            # serializer = SubscriptionSerializer(
            #     author, data=request.data,
            #     context={'request': request}
            # )
            # serializer.is_valid(raise_exception=True)
            # if Subscription.objects.filter(user=user, author=author).exists():
            #     return Response(
            #         {'error': 'Уже существует подписка на данного автора.'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            # Subscription.objects.get_or_create(user=user, author=author)
            # return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            return self._delete_connection(Subscription, request.user, pk)
            # try:
            #     subscription = Subscription.objects.get(
            #         user=user, author=author
            #     )
            #     subscription.delete()
            # except Subscription.DoesNotExist:
            #     return Response(
            #         {'error': 'Подписка на данного автора не существует.'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            # return Response(status=status.HTTP_204_NO_CONTENT)/

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписка."""
        pages = self.paginate_queryset(
            User.objects.filter(subscribing__user=self.request.user)
        )
        serializer = SubscriptionSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
