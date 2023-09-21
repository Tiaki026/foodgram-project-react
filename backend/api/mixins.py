from rest_framework.serializers import ModelSerializer
from django.db.models import Model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status


class AddOrDeleteMixin:
    """Добавление и удаление связей."""

    serializer_class = ModelSerializer
    model_class = Model

    def _add_connection(self, user, id):
        recipe = get_object_or_404(self.model_class, id=id)
        if self.model_class.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'detail': 'Дейсвтие невозможно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.model_class.objects.create(user=user, recipe=recipe)
        serializer = self.serializer_class(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers={'detail': 'Связь успешно создана'}
        )

    def _delete_connection(self, user, id):
        obj = self.model_class.objects.filter(user=user, recipe__id=id)
        if obj.exists():
            obj.delete()
            return Response(
                {'detail': 'Связь успешно удалена'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'detail': 'Дейсвтие невозможно'},
            status=status.HTTP_400_BAD_REQUEST
        )