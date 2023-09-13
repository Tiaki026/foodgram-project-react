from django.core.management import BaseCommand

from recipes import models


class CreateTags(BaseCommand):
    """Создание тегов для БД."""

    class Meta:
        model = models.Tag
        fields = ['name', 'color', 'slug']

    def create_tags(self):
        """Создание тегов для БД."""
        tags_data = [
            {'name': 'завтрак', 'color': '#FFA500', 'slug': 'breakfast'},
            {'name': 'обед', 'color': '#008B8B', 'slug': 'dinner'},
            {'name': 'ужин', 'color': '#800080', 'slug': 'evening meal'},
        ]

        for tag_data in tags_data:
            tag, created = models.Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults={
                    'color': tag_data['color'],
                    'slug': tag_data['slug'],
                }
            )

            if created:
                print(f'Тег "{tag.name}" успешно создан.')
            else:
                print(f'Тег "{tag.name}" уже существует.')

        print("Создание тегов завершено.")
