from .validators import validate_tag, validate_hex_color
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название',
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
        ordering = ['name']

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
        ordering = ['name']
        constraints = [models.UniqueConstraint(
            fields=('name', 'measurement_unit'),
            name='unique_for_ingredient',
            )
        ]

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipe',
        through='AmountRecipeIngredients',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        verbose_name='Список тегов',
    )
    image = models.ImageField(
        verbose_name='Картинка, закодированная в Base64',
        upload_to='recipes/',
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
        ordering = ['-id']
        constraints = [models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            )
        ]

    def __str__(self) -> str:
        return f'{self.name} {self.author.username}'


class AmountRecipeIngredients(models.Model):
    """Общее количество ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Наименование рецептов',
        related_name='recipe_amount',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='ingredients_amount',
        on_delete=models.CASCADE,
        verbose_name='Наименование ингредиентов',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Общее количество ингредиентов в рецепте'
        verbose_name_plural = 'Общее количество ингредиентов в рецептах'
        ordering = ['recipe']
        constraints = [models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_ingredients'
            )
        ]

    def __str__(self) -> str:
        return (
            f'{self.amount} > {self.ingredients.measurement_unit}'
        )


class Favorite(models.Model):
    """Избранные рецеты."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='in_favorite',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_favorite'
            )
        ]

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
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping'
            )
        ]

    def __str__(self) -> str:
        return (
            f'Пользователь {self.user} добавил {self.recipe} в список покупок.'
        )
