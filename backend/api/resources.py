from import_export import resources
from recipes.models import Ingredient


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
