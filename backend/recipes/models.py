from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .common import upload_to
from .validators import validate_hex_color, validate_tag

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        db_index=False,
        verbose_name='Цвет в HEX',
        unique=True,
        validators=[validate_hex_color]
    )
    slug = models.CharField(
        max_length=200,
        db_index=False,
        verbose_name='Уникальный слаг',
        unique=True,
        validators=[validate_tag]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self) -> str:
        return f'Тег {self.name} {self.color}'


class Ingredient(models.Model):
    """Модель ингредиетов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='AmountRecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to=upload_to,
    )
    text = models.TextField(
        max_length=200,
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания рецепта',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'resipes'
        ordering = ['-id']
        unique_together = [('name', 'author')]

    def __str__(self) -> str:
        return f'{self.name} {self.author.username}'


class AmountRecipeIngredient(models.Model):
    """Количество ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_amount',
        verbose_name='Наименование рецептов',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Наименование ингредиента',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество ингредиентов',
    )

    class Meta:
        verbose_name = 'Количество ингредиентов в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецептах'
        ordering = ['recipe']
        unique_together = [('recipe', 'ingredient')]

    def __str__(self) -> str:
        return (
            f'{self.amount} -> {self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    """Избранные рецеты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorited',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='in_favorited',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        unique_together = [('user', 'recipe')]

    def __str__(self) -> str:
        return f'Пользователь {self.user} добавил в избраное {self.recipe}.'


class ShoppingCart(models.Model):
    """Список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Список покупок',
        related_name='in_shopping',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        unique_together = [('user', 'recipe')]

    def __str__(self) -> str:
        return (
            f'Пользователь {self.user} добавил {self.recipe} в список покупок.'
        )
