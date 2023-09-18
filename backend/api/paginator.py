from rest_framework.pagination import PageNumberPagination


class CustomUserPagination(PageNumberPagination):
    """Настройка отображения пользователя для API."""

    page_size = 1


class CustomRecipePagination(PageNumberPagination):
    """Настройка отображения рецептов на странице."""

    page_query_param = 'limit'
