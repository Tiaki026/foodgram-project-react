from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .forms import RecipeForm
from .models import (AmountRecipeIngredients, Favorite, Ingredient, Recipe,
                     ShoppingCart, Tag)


@admin.register(AmountRecipeIngredients)
class AmountRecipeIngredientsAdmin(admin.ModelAdmin):
    """Администрирование общего количесвта ингридиентов."""

    # list_display = ['recipe', 'ingredients', 'amount']
    # list_filter = ['recipe', 'ingredients']
    # search_fields = ['recipe__name', 'ingredient__name']
    fields = ['recipe','ingredients', 'amount']
    pass


class AmountRecipeIngredientsInline(admin.TabularInline):
    """Класс связанных объектов."""

    model = AmountRecipeIngredients
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов."""

    list_display = [
        'name', 'id', 'author', 'is_favorited', 'is_image'
    ]
    list_filter = ['author', 'name', 'tags']
    search_fields = ['author__username', 'name', 'tags__name']
    raw_id_fields = ['author']
    # form = RecipeForm
    inlines = [AmountRecipeIngredientsInline]
    fields = [
        'name', 'author', 'tags', 'image',
        'text', 'cooking_time'
    ]

    @admin.display(description='Избранное')
    def is_favorited(self, obj: Recipe) -> bool:
        """Проверка избранных рецептов.

        Проверяет, есть ли избранные рецепты у пользователя
        и выдает количесвто.
        """
        count = obj.in_favorited.count()
        exist = obj.in_favorited.exists()
        if count > 0:
            return f'{exist} ({count})'
        return exist

    @admin.display(description='Картинка')
    def is_image(self, obj: Recipe):
        """Превью картинки."""
        return format_html(
            '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
            obj.image.url
        )
        # return mark_safe(f'<img src={obj.image.url} width="50" hieght="50"')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов."""

    list_display = ['name', 'measurement_unit']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Администрирование тегов."""

    list_display = ['name', 'color', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ['name']}


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Администрирование списка покупок."""

    list_display = ['user', 'recipe']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Администрирование избранных рецептов."""

    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
