from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """Разренение для автора и администратора.

    Автору и администратору возможно создание, редактирование, удаление.
    Остальным только чтение.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in SAFE_METHODS
            or request.user.is_superuser
            and request.user.is_staff
        )


class IsAdminOrReadOnly(BasePermission):
    """Разренение для администратора.

    Администратору возможно создание, редактирование, удаление.
    Остальным только чтение.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_staff
            and request.user.is_superuser
        )
