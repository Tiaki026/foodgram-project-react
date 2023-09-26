from typing import Type

from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, DjangoModelPermissions,
                                        IsAuthenticated)
from rest_framework.response import Response
from rest_framework.request import Request

from recipes.models import (Favorite, Ingredient,
                            Recipe, ShoppingCart, Tag, User)

from .filters import IngredientFilter, RecipeFilter
from .generator import IngredientsFileGenerator
from .mixins import RecipeMixin, UserMixin
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


class RecipeViewSet(viewsets.ModelViewSet, RecipeMixin):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.select_related('author')
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    filterset_class = RecipeFilter
    # pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]

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
    def favorite(self, request, pk: int):
        """Добавление и удаление из избранного."""
        self.model_class = Favorite
        return self._add_delete_method(request, self.request.user, pk)

    @action(
        detail=True, permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE']
    )
    def shopping_cart(self, request, pk: int):
        """Добавление и удаление из списка покупок."""
        self.model_class = ShoppingCart
        return self._add_delete_method(request, self.request.user, pk)

    @action(
        detail=False, methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request: Request) -> HttpResponse:
        """Скачивание файла с ингредиентами в нескольких форматах."""
        user = request.user
        if not user.shopping.exists():
            return Response(
                f'Это для {user.username}',
                status=status.HTTP_400_BAD_REQUEST
            )
        file_format = request.query_params.get('format')
        file_generator = IngredientsFileGenerator(user)
        format_to_method = {
            'pdf': file_generator.generate_pdf,
            'doc': file_generator.generate_doc,
            'txt': file_generator.generate_txt
        }
        if file_format in format_to_method:
            response = format_to_method[file_format]()
            response['Content-Disposition'] = (
                f'attachment;'
                f'filename="ingredient_list.{file_format}"'
            )
            return response


class UserViewSet(UserViewSet, UserMixin):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = [DjangoModelPermissions]

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id) -> Response:
        """Создание и удаление подписок."""
        return self._add_delete_method(request, self.request.user, id)

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
