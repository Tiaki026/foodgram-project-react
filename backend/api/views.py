from typing import Type

from django.db.models import Sum, QuerySet
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, DjangoModelPermissions,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.request import Request

from recipes.models import (AmountRecipeIngredients, Favorite, Ingredient,
                            Recipe, ShoppingCart, Tag, User)
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .generator import IngredientsFileGenerator
from .mixins import RecipeMixin
from .paginator import CustomPagination
from .permissions import IsAdminOrOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          TagSerializer)


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

    # def get_queryset(self) -> QuerySet:
    #     queryset = self.queryset
    #     name = self.request.query_params.get('name')

    #     if name:
    #         return queryset.filter(name__istartswith=name)
    #     return queryset


class RecipeViewSet(viewsets.ModelViewSet, RecipeMixin):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    filterset_class = RecipeFilter
    serializer_class = RecipeSerializer

    def get_serializer_class(self) -> Type[RecipeSerializer]:
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer) -> None:
        serializer.save(author=self.request.user)

    @action(
        detail=True, permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE']
    )
    def favorite(self, request: Request, pk: int) -> Response:
        """Добавление и удаление из избранного."""
        self.model_class = Favorite
        if request.method == 'POST':
            return self._add_connection(request.user, pk)
        elif request.method == 'DELETE':
            return self._delete_connection(request.user, pk)
        return Response(
            {'detail': 'Метод не поддерживается'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(
        detail=True, permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE']
    )
    def shopping_cart(self, request: Request, pk: int) -> Response:
        """Добавление и удаление из списка покупок."""
        self.model_class = ShoppingCart
        if request.method == 'POST':
            return self._add_connection(request.user, pk)
        elif request.method == 'DELETE':
            return self._delete_connection(request.user, pk)
        return Response(
            {'detail': 'Метод не поддерживается'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(
        detail=False, methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request: Request) -> HttpResponse:
        """Скачивание файла с ингредиентами в нескольких форматах."""
        user = request.user
        recipe_name = AmountRecipeIngredients.objects.filter(
            recipe__in_shopping__user=user
        ).values('recipe__name').first().get('recipe__name', 'Без названия')
        shopping_cart = [
            f'Список ингредиентов для "{user.username}"\n'
            f'Готовим "{recipe_name}"\n'
            f'Для этого понадобятся:\n'
        ]
        if not user.shopping.exists():
            return Response(
                f'Это для {user.username}',
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredient = (
            AmountRecipeIngredients.objects.filter(
                recipe__in_shopping__user=user
            ).values(
                'ingredients__name',
                'ingredients__measurement_unit'
            ).annotate(amount=Sum('amount'))
        )
        for ingredients in ingredient:
            shopping_cart.append(
                f'{ingredients["ingredients__name"]}: '
                f'{ingredients["amount"]} '
                f'{ingredients["ingredients__measurement_unit"]}'
            )
        format = request.query_params.get('format')
        print(f"Received format: {format}")
        file_generator = IngredientsFileGenerator(shopping_cart)
        if format == 'pdf':
            return file_generator.generate_pdf(shopping_cart)
        elif format == 'doc':
            return file_generator.generate_doc(shopping_cart)
        elif format == 'txt':
            return file_generator.generate_txt(shopping_cart)
        return HttpResponse(shopping_cart)


class UserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = [DjangoModelPermissions]

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request: Request, id) -> Response:
        """Создание и удаление подписок."""
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            if user == author:
                return Response(
                    f'{author} не может подписаться на {author}',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    f'Вы уже подписаны на {author}.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(user=user, author=author)
            self.get_serializer(author)
            return Response(
                f'Вы подписались на {author}.',
                status=status.HTTP_201_CREATED,
            )
        elif request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    'Действие невозможно',
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(
                f'Вы отписались от {author}',
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                'Метод не поддерживается',
                status=405
            )

    @action(
        detail=False, methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request: Request) -> Response:
        """Подписки пользователя."""
        user = request.user
        subscriptions = User.objects.filter(
            subscribing__user=user
        ).prefetch_related('recipes')
        paginated_queryset = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)
