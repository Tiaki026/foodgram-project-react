from rest_framework.pagination import PageNumberPagination


class CustomUserPagination(PageNumberPagination):
    """Настройка отображения пользователя для API."""

    page_size = 1
