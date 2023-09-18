from django import forms

from .models import Recipe, Ingredient


class RecipeForm(forms.ModelForm):
    """Форма ингредиентов для создания рецепта в админке."""

    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = Recipe
        fields = '__all__'
