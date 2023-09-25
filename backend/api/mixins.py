from rest_framework.serializers import ModelSerializer
from django.db.models import Model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from recipes.models import Recipe, User


class RecipeMixin:
    """Миксин добавления / удаления в избранное и список покупок."""

    serializer_class = ModelSerializer
    model_class = Model

    def _add_delete_method(self, request, user, pk: int):
        """Метод создания / удаления."""
        if request.method == 'POST':
            if self.model_class.objects.filter(
                user=user, recipe__id=pk
            ).exists():
                return Response(
                    {'detail': 'Действие невозможно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = get_object_or_404(Recipe, id=pk)
            self.model_class.objects.create(user=user, recipe=recipe)
            serializer = self.serializer_class(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers={'detail': 'Связь успешно создана'}
            )

        recipe = self.model_class.objects.filter(
            user=user, recipe__id=pk
        )
        if recipe.exists():
            recipe.delete()
            return Response(
                {'detail': 'Связь успешно удалена'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'detail': 'Действие невозможно'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserMixin:
    """Миксин создания / удаления."""

    serializer_class = ModelSerializer
    model_class = Model

    def _add_delete_method(self, request, user, id: int):
        """Метод создания и удаления подписки."""
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            if self.model_class.objects.filter(
                user=user, author=author
            ).exists():
                return Response(
                    f'Вы уже подписаны на {author}.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.model_class.objects.create(user=user, author=author)
            return Response(
                f'Вы подписались на {author}.',
                status=status.HTTP_201_CREATED,
            )
        get_object_or_404(
            self.model_class,
            user=user,
            author=author
        ).delete()
        return Response(
            f'Вы отписались от {author}',
            status=status.HTTP_204_NO_CONTENT
        )
