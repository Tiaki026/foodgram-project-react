
# def upload_to(instance, filename):
#     """Метод загрузки картинки."""
#     instance.save() 
#     user = instance.author.username
#     user_id = instance.author.pk
#     recipe_name = instance.name
#     recipe_id = instance.id
#     tags_slug = ''.join([tag.slug for tag in instance.tags.all()[:3]])
#     return (
#         f'recipes/{user}_{user_id}_{recipe_name}'
#         f'_{recipe_id}_{tags_slug}/{filename}'
#     )


def upload_to(instance, filename):

    extension = filename.split('_')[-1]

    tags_slug = ''.join([tags.slug for tags in instance.tags.slug()[:3]])

    return f"media/recipes/{0}_{1}_{2}.{3}".format(
        instance._meta.module_name,
        instance._meta.module_author,
        instance.name,
        extension
        )
