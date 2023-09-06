from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'ingredient', IngredientViewSet, basename='ingredient')
router.register(r'recipe', RecipeViewSet, basename='recipe')
router.register(r'tag', TagViewSet, basename='tag')

urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
