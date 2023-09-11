from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .generator import IngredientsFileGenerator
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (
    SubscriptionSerializer, TagSerializer,
    RecipeSerializer,
    IngredientSerializer, UserSerializer
)
from recipes.models import Ingredient, Recipe, Tag, User
from users.models import Subscription
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions


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


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]

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


class UserViewSet(
    viewsets.ModelViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    """Вьюсет пользователя."""

    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [DjangoModelPermissions]
    link_model = Subscription

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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscription(self, request):
        """Подписка."""
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

# class UserViewSet(views.UserViewSet):
#     """Вьюсет пользователя."""

#     queryset = User.objects.all()
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserListSerializer

#     def get_serializer_class(self):
#         if self.action == 'list':
#             return SubscriptionSerializer
#         return UserListSerializer
    
