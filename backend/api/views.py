from django.db.models import Q
from django.http import HttpResponse

from rest_framework import viewsets, status
from rest_framework.decorators import action
from .generator import IngredientsFileGenerator
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (
    SubscriptionSerializer, TagSerializer,
    RecipeSerializer, IngredientSerializer,
    CustomUserSerializer
)
from .paginator import CustomUserPagination
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag, User
from users.models import Subscription
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

    @action(detail=False, methods=['get'])
    def ingredient_search(query):
        """Поиск ингредиентов."""
        return Ingredient.objects.filter(name__startswith=query)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]

    # @action(detail=False, methods=['post'])
    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop('tags')
        ingredients_query = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)

        ingredients = Ingredient.objects.filter(name__in=ingredients_query)
        self.ingredients_set(recipe, ingredients)

        return recipe

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
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = CustomUserPagination

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
