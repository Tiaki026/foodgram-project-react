from io import BytesIO

from django.db.models import Sum
from django.http import HttpResponse
from docx import Document
from recipes.models import AmountRecipeIngredients
from reportlab.pdfgen import canvas


class ShoppingCartFileGenerator:
    """Класс генерации списка покупок в форматах pdf, txt, doc."""

    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.recipe_names = self.get_recipe_name()
        self.filename = f'{self.user.username}_ingredient_list'

    def get_recipe_name(self):
        recipes = AmountRecipeIngredients.objects.filter(
            recipe__in_shopping__user=self.user
        ).values('recipe__name').distinct()
        return [recipe_info['recipe__name'] for recipe_info in recipes]

    def create_shopping_cart_list(self):
        """Создание списка покупок."""
        recipe_names = [
            f'"{recipe_name}"' for recipe_name in self.recipe_names
        ]
        recipe_names_str = ", ".join(recipe_names)
        shopping_cart = [
            f'Список ингредиентов для '
            f'"{self.user.first_name} {self.user.last_name}"\n'
            f'Готовим {recipe_names_str}\n'
            f'Для этого понадобятся:\n'
        ]
        ingredient = (
            AmountRecipeIngredients.objects.filter(
                recipe__in_shopping__user=self.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(amount=Sum('amount'))
        )
        for ingredients in ingredient:
            shopping_cart.append(
                f'{ingredients["ingredient__name"]}: '
                f'{ingredients["amount"]} '
                f'{ingredients["ingredient__measurement_unit"]}'
            )
        return shopping_cart

    def generate_pdf(self, shopping_cart) -> HttpResponse:
        """Генератор формата pdf."""
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        for shopping_c in shopping_cart:
            p.drawString(100, p._y, shopping_c)
            p.showPage()

        p.save()
        buffer.seek(0)
        format = 'pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; {self.filename}.{format}'
        )
        response.write(buffer.getvalue())

        return response

    def generate_txt(self, shopping_cart) -> HttpResponse:
        """Генератор формата txt."""
        content = '\n'.join(shopping_cart)
        format = 'txt'
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; {self.filename}.{format}'
        )
        response.write(content.encode('utf-8'))

        return response

    def generate_doc(self, shopping_cart) -> HttpResponse:
        """Генератор формата doc."""
        document = Document()
        for shopping_c in shopping_cart:
            document.add_paragraph(shopping_c)

        buffer = BytesIO()
        document.save(buffer)
        # content_type = 'application/msword'
        format = 'doc'
        response = HttpResponse(content_type='application/msword')
        response['Content-Disposition'] = (
            f'attachment; {self.filename}.{format}'
        )
        response.write(buffer.getvalue())

        return response
