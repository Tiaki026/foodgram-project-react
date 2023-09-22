from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.decorators import action
from .generator import IngredientsFileGenerator
from .permissions import IsAdminOrReadOnly, IsAdminOrOwnerOrReadOnly
from .serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipeCreateSerializer, RecipeReadSerializer
)
from .mixins import RecipeMixin
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
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import DjangoModelPermissions
from django.shortcuts import get_object_or_404


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
    

class RecipeViewSet(viewsets.ModelViewSet, RecipeMixin):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True, permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE']
    )
    def favorite(self, request, pk):
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
    def shopping_cart(self, request, pk):
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

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Скачивание файла с ингредиентами в нескольких форматах."""
        user = request.user
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


class UserViewSet(UserViewSet):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = [DjangoModelPermissions]

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Создание и удаление подписок."""
        self.model_class = Subscription
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == 'POST':
            if user == author:
                return Response(
                    f'{author} не может подписаться на {author}',
                    status=400
                )
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    f'Вы уже подписаны на {author}.',
                    status=400
                )
            Subscription.objects.create(user=user, author=author)
            self.get_serializer(author)
            return Response(
                self.get_serializer(author),
                f'Вы подписались на {author}.',
                status=201
            )
        elif request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    'Действие невозможно',
                    status=400
                )
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(
                f'Вы отписались от {author}',
                status=204
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
    def subscriptions(self, request):
        user = self.request.user
        subscriptions = User.objects.filter(
            subscribing__user=user
        ).prefetch_related('recipes')
        paginated_queryset = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)
