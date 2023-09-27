from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """Разренение для автора и администратора.

    Автору и администратору возможно создание, редактирование, удаление.
    Остальным только чтение.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            and request.user.is_superuser
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


class IsAdminOrOwnerOrReadOnly(BasePermission):
    """Разренение для администратора и владельца."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user == obj.author
            or request.user.is_staff
            and request.user.is_superuser
        )
