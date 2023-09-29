from django.contrib import admin
from django.utils.html import format_html

from .models import (AmountRecipeIngredients, Favorite, Ingredient, Recipe,
                     ShoppingCart, Tag)


def tag_color(tag: Tag):
    """Превью цвета тегов."""
    color_map = {
        'breakfast': '🟠',
        'dinner': '🟢',
        'evening meal': '🟣',
    }

    return f'{tag.name} {color_map.get(tag.slug, "")}'


@admin.register(AmountRecipeIngredients)
class AmountRecipeIngredientsAdmin(admin.ModelAdmin):
    """Администрирование общего количесвта ингридиентов."""

    fields = ['recipe', 'ingredients', 'amount']


class AmountRecipeIngredientsInline(admin.TabularInline):
    """Класс связанных объектов."""

    model = AmountRecipeIngredients
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов."""

    list_display = [
        'name', 'id', 'author', 'pub_date',
        'color_preview', 'is_favorited', 'is_image',
    ]
    list_filter = ['author', 'name', 'tags']
    search_fields = ['author__username', 'name', 'tags__name']
    raw_id_fields = ['author']
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
        if count > 0:
            return f'{count} ⭐️'

    @admin.display(description='Картинка')
    def is_image(self, obj: Recipe):
        """Превью картинки."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 90px; max-width: 90px;" />',
                obj.image.url
            )
        else:
            return 'Нет изображения'

    @admin.display(description='Теги')
    def color_preview(self, obj: Recipe):
        """Цвет тега в рецептах."""
        tags = obj.tags.all()
        return ', '.join([tag_color(tag) for tag in tags])


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов."""

    list_display = ['name', 'measurement_unit']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Администрирование тегов."""

    list_display = ['name', 'color', 'color_preview', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ['name']}

    @admin.display(description='Цвет тега')
    def color_preview(self, obj: Tag):
        """Цвет тега."""
        return tag_color(obj)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Администрирование списка покупок."""

    list_display = ['user', 'recipe']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Администрирование избранных рецептов."""

    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
