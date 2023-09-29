from .utils import query_debugger
from recipes import models


@query_debugger
def bld():
    # qs = Recipe.objects.all()
    qs = models.Recipe.objects.select_related('author')
    # qs = Recipe.objects.select_related('author').select_related('ingredients')
    # qs = Recipe.objects.select_related('author', 'ingredients')

    print(qs.query)

    recipes = []
    for item in qs:
        recipes.append({
            'id': item.id, 
            'name': item.name, 
            'author': item.author, 
            'ingredients': item.ingredients,
            'tags': item.tags, 
            'image': item.image, 
            'cooking_time': item.cooking_time,
            'create': item.create,
            'update': item.update
            # 'in_favorited': item.in_favorited, 
            # 'shopping_cart': item.in_shopping
        })
    return recipes