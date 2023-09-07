from io import BytesIO

from django.http import HttpResponse
from docx import Document
from reportlab.pdfgen import canvas


class IngredientsFileGenerator:
    """Класс генерации файлов."""

    def __init__(self, ingredients):
        self.ingredients = ingredients

    def generate_pdf(self):
        """Генератор формата pdf."""
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        for ingredient in self.ingredients:
            p.drawString(100, p._y, ingredient)
            p.showPage()

        p.save()
        buffer.seek(0)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="ingredient_list.pdf"'
        )
        response.write(buffer.getvalue())

        return response

    def generate_txt(self):
        """Генератор формата txt."""
        content = '\n'.join(self.ingredients)

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="ingredient_list.txt"'
        )
        response.write(content.encode('utf-8'))

        return response

    def generate_doc(self):
        """Генератор формата doc."""
        document = Document()
        for ingredient in self.ingredients:
            document.add_paragraph(ingredient)

        buffer = BytesIO()
        document.save(buffer)
        content_type = 'application/msword'

        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = (
            'attachment; filename="ingredient_list.doc"'
        )
        response.write(buffer.getvalue())

        return response
