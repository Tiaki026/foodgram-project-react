from .models import (
    Favorite, Ingredient,
    Recipe, ShoppingCart,
    AmountRecipeIngredients, Tag
)
from django.contrib import admin


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов."""

    list_display = (
        'name', 'id', 'author',
        'add_in_favorite',
    )
    readonly_fields = ['add_in_favorite']
    list_filter = ('author', 'name', 'tags',)
    search_fields = ['author__username']
    raw_id_fields = ['author']

    @admin.display(description='Количество в избранных')
    def add_in_favorite(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Администрирование ингредиентов."""

    list_display = ('name', 'measurement_unit',)
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Администрирование тегов."""

    list_display = ('name', 'color', 'slug',)
    search_fields = ['name']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Администрирование списка покупок."""

    list_display = ('user', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Администрирование избранных рецептов."""

    list_display = ('user', 'recipe',)
    search_fields = ['user__username', 'recipe__title']


@admin.register(AmountRecipeIngredients)
class AmountRecipeIngredientsAdmin(admin.ModelAdmin):
    """Администрирование общего количесвта ингридиентов."""

    list_display = ('recipe', 'ingredients', 'amount',)
    list_filter = ['recipe', 'ingredients']
    search_fields = ['recipe__title', 'ingredient__name']
