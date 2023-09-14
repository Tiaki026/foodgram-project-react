import csv
import json

csv_file = 'ingredients.csv'
json_file = 'ingredients.json'
output_file = 'combined_ingredients.json'

csv_data = []
with open(csv_file, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)
    for i, row in enumerate(reader, start=1):
        csv_data.append({
            'id': i,
            'name': row[0],
            'measurement_unit': row[1]
        })

with open(json_file, 'r', encoding='utf-8') as file:
    json_data = json.load(file)
    max_id = max(
        ingredient['id'] for ingredient in csv_data
    ) if csv_data else 0

    for ingredient in json_data:
        ingredient['id'] = max_id + 1
        max_id += 1

combined_data = []
for ingredient in csv_data + json_data:
    combined_data.append({
        "model": "recipes.ingredient",
        "id": ingredient["id"],
        "fields": {
            "name": ingredient["name"],
            "measurement_unit": ingredient["measurement_unit"]
        }
    })

with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(combined_data, file, indent=4, ensure_ascii=False)

print(f'Файл {output_file} успешно создан.')