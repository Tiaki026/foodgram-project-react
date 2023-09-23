"""Создание тегов для БД.

tags.json
"""
import json

tags_data = [
    {'name': 'завтрак', 'color': '#FFA500', 'slug': 'breakfast'},
    {'name': 'обед', 'color': '#008B8B', 'slug': 'dinner'},
    {'name': 'ужин', 'color': '#800080', 'slug': 'evening meal'},
]

tags = []
for i, tag_data in enumerate(tags_data, start=1):
    tag = {
        'model': 'recipes.tag',
        'pk': i,
        'fields': tag_data
    }
    tags.append(tag)

with open('tags.json', 'w', encoding='utf-8') as file:
    json.dump(tags, file, ensure_ascii=False, indent=4)

print("JSON файл с тегами успешно создан.")
