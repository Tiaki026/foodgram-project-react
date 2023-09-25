def upload_to(instance, filename):
    """Метод загрузки картинки пользователями.

    Картинка будет храниться в папке
    recipes/папка с именем и фамилией пользователя/
    """
    return (
        f'recipes/{instance.author.first_name} {instance.author.last_name}/'
        f'{instance.name}.{filename}'.format()
    )
