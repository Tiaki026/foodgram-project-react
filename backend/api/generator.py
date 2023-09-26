from io import BytesIO

from django.http import HttpResponse
from docx import Document
from reportlab.pdfgen import canvas
from recipes.models import AmountRecipeIngredients
from django.db.models import Sum


class IngredientsFileGenerator:
    """Класс генерации списка покупок в форматах pdf, txt, doc."""

    def __init__(self):
        self.shopping_cart = self.create_shopping_cart_list()

    def create_shopping_cart_list(self, request):
        user = request.user
        recipe_name = AmountRecipeIngredients.objects.filter(
            recipe__in_shopping__user=user
        ).values('recipe__name').first().get('recipe__name', 'Без названия')
        shopping_cart = [
            f'Список ингредиентов для "{user.username}"\n'
            f'Готовим "{recipe_name}"\n'
            f'Для этого понадобятся:\n'
        ]
        ingredient = (
            AmountRecipeIngredients.objects.filter(
                recipe__in_shopping__user=user
            ).values(
                'ingredients__name',
                'ingredients__measurement_unit'
            ).annotate(amount=Sum('amount'))
        )
        for ingredients in ingredient:
            shopping_cart.append(
                f'{ingredients["ingredients__name"]}: '
                f'{ingredients["amount"]} '
                f'{ingredients["ingredients__measurement_unit"]}'
            )
        return shopping_cart

    def generate_pdf(self) -> HttpResponse:
        """Генератор формата pdf."""
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        for shopping_c in self.shopping_cart:
            p.drawString(100, p._y, shopping_c)
            p.showPage()

        p.save()
        buffer.seek(0)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="ingredient_list.pdf"'
        )
        response.write(buffer.getvalue())

        return response

    def generate_txt(self) -> HttpResponse:
        """Генератор формата txt."""
        content = '\n'.join(self.shopping_cart)

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="ingredient_list.txt"'
        )
        response.write(content.encode('utf-8'))

        return response

    def generate_doc(self) -> HttpResponse:
        """Генератор формата doc."""
        document = Document()
        for shopping_c in self.shopping_cart:
            document.add_paragraph(shopping_c)

        buffer = BytesIO()
        document.save(buffer)
        content_type = 'application/msword'

        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = (
            'attachment; filename="ingredient_list.doc"'
        )
        response.write(buffer.getvalue())

        return response
