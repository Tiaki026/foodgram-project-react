# Продуктовый помощник Foodgram
## Описание
Foodgram — социальная сеть для обмена рецептами. Это полностью рабочий проект, который состоит из бэкенд-приложения на Django и фронтенд-приложения на React. В нем Вы можете разместить рецепты вкусных блюд, подписаться на понравившихся авторов, добавлять самые лучшие рецепты вкусных блюд в избранное, а так же создавать список покупок добавляя туда рецепты. Проект сам посчитает нужные ингредиенты из рецептов, который Вы можете скачать.

## Процесс разработки, особенности и трудности
В проекте присутствует 3 приложения - users, recipes, api.
В users - модели и админка пользователей и подписок. Решил вынести их отдельно от рецептов, так как пользователя связаны с регистрацией и аутентификацией, а подписки связаны с пользователями.
В recipes - модели рецептов и админка.
Остальная логика в API.
Самое сложное, наверное, это вспомнить все чему тебя учили 9 месяцев в [Яндекс практикум](https://github.com/yandex-praktikum). Сначала проект казался крайне трудным, сложным и непонятным. Начинал с создания моделей, потом админки и после уже API. Каждый раз хотелось посмотреть как выглядит сайт, но увидел только спустя несколько недель.
Самая большая ошибка во всей разработке - я забывал пушиться на GitHub. Немного меняя код, сталкивался с тем, что все или некая часть перестает работать. Приходлось вспоминать, как оно было ранее. Можно было часами искать ошибку. Не забывайте пушить проект, это сэкономит ваше время и нервы. Таким образом проект напишете гораздо быстрее. Не забывайте делать перерывы, отдохнувший человек быстрее соображает.
Django - это кропотливый процесс, и лучше всего изучать и совершенствовать свои навыки.

## Стек технологий
- ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

  Python: Язык программирования
- ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

  Django: Фреймворк для создания веб-приложений
- ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)

  Django Rest Framework: Расширение для Django, предоставляющее функциональность REST API
- ![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
  Ubuntu: Операционная система
- ![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?&style=for-the-badge&logo=postgresql&logoColor=white)

PostgreSQL: База данных
- ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)

  JavaScript: Язык программирования для создания динамических веб-страниц
- ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)

  React: JavaScript-библиотека для создания пользовательских интерфейсов
- ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

  Nginx: Веб-сервер и обратный прокси-сервер
- ![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)

  Gunicorn: WSGI-сервер для запуска веб-приложений на Python
- ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
  
  Docker: Платформа для создания, развертывания и управления приложениями в изолированных средах.

## Как воспользоваться проектом
### Клонирование проекта с GitHub на компьютер
`git@github.com:Tiaki026/foodgram-project-react.git`

### Настройка бэкенд-приложения
1.	Перейдите в директорию бэкенд-приложения проекта.
```
cd foodgram-project-react/backend/
```
2.	Создайте виртуальное окружение.
    Linux
```
python3 -m venv venv
```
    Windows
```
python -m venv venv
```
3.	Активируйте виртуальное окружение.
    Linux
```
source venv/bin/activate
```
    Windows
```
source venv/Scripts/activate
```
4.	Установите зависимости.
```
pip install -r requirements.txt
```
5. Создайте .env [пример файла]()
6.	Примените миграции.
    Linux
```
python3 manage.py migrate
```
    Windows
```
python manage.py migrate
```
7. Создайте админа
    Linux
```
python3 manage.py createsuperuser
```
    Windows
```
python manage.py createsuperuser
```

### Загрузка базы данных
Находясь в папке backend выполните команды. Скрипты создадут json-файлы для ингредиентов и тегов.
```
python data/script_ingredients.py
python data/script_tags.py
python manage.py loaddata data/combined_ingredients.json
python manage.py loaddata data/tags.json
```

### Docker
Важно знать, что докер не запустится без активного виртуального ядра.
Настройка находится в BIOS. Здесь уже все индивидуально. Чаще всего это настройка процессора -> Virtualization.

Установите Docker:
 - Для Windows [скачать](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=dd-smartbutton&utm_location=module)
 - Для Linux
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin 
```
Создаем Dockerfile

 [Dockerfile_backend](https://github.com/Tiaki026/foodgram-project-react/blob/master/backend/Dockerfile)
 
 [Dockerfile_frontend](https://github.com/Tiaki026/foodgram-project-react/blob/master/frontend/Dockerfile)

 [Conf nginx](https://github.com/Tiaki026/foodgram-project-react/blob/master/infra/nginx.conf)

 Создаем docker-compose.yml

 [docker-compose](https://github.com/tetrapack55/foodgram-project-react/blob/master/infra/docker-compose.yml)

Команды для проверки docker-compose
```
docker compose up   # Запускает контейнеры
docker compose exec backend python manage.py migrate    # Миграции в контейнере backend
docker compose down # Удаляет контейнеры
docker compose up --build   # Создает новые контейнеры и запускает их
```

Если запуск локальный, то можно воспользоваться docker-compose.yml. В папке с файлом выполнить команду `docker compose up --build`.
Для того чтобы развернуть проект на сервере - создаем main.yml. Проще это сделать на github, после чего выполнить команду `git pull`. Файл окажется в папке проекта.

 [main.yml]()
При заполнении файла создаются секретные ключи, которые хранятся на Вашем github в разеделе <папка проекта> -> settings -> secterts and variables -> actions.

`DOCKER_USERNAME` - имя пользователя от DockerHub
`DOCKER_PASSWORD` - пароль от DockerHub
`HOST` - IP-адрес вашего сервера
`USER` - имя пользователя сервера
`SSH_KEY` - закрытый SSH-ключ
`SSH_PASSPHRASE` - пароль от сервера
`TELEGRAM_TO` - ID telegram-аккаунта
`TELEGRAM_TOKEN` - токен бота, который пришлет сообщение в дальнейшем

Если в [main.yml] все написано верно, то после команды `git push` на github в actions начнется тестирование образов (если имеются тесты), создадутся образы Docker, запушатся на Dockerhub, после загрузятся на удаленный сервер и запустятся. А так же в телеграм отправится сообщение от бота, что проект успешно задеплоен.

## Как убидиться что проект работает?
Для этого вам понадобится [Postman](https://dl.pstmn.io/download/latest/win64)
В проекте присутствует [файл](https://github.com/Tiaki026/foodgram-project-react/blob/master/postman-collection/diploma.postman_collection.json) для postman, с его помощью можно проверить работоспособность.

P.S.: Не все тесты настроены хорошо, для некоторых нужно будет прописать переменные.
В Environment создайте новое окружение `New Environment`. В `Variable` напишите название переменных, в `Initial value` их значение.
Например
```
thirdTagSlug                evening meal
secondTagSlug               dinner
ingredientNameFirstLatter   абрикос
```

### Подготовка Django-проекта к запуску коллекции:

1. Проверьте, что виртуальное окружение развёрнуто и активировано, зависимости проекта установлены.
2. Для локальной проверки API в настройках `settings.py` подключите в качестве базы данных SQLite3 
и установите значение `DEBUG = True`.
3. Выполните миграции; создайте в базе данных как минимум 2 ингредиента и 3 тега.
4. Запустите веб-сервер разработки.

*После подготовки проекта создайте копию файла базы данных `db.sqlite3`: 
она может пригодиться в случае сбоя в работе.*

### Запуск коллекции:

1. После выполнения предыдущих шагов, в левой части окна Postman во вкладке `Collections` появилась импортированная коллекция.
Наведите на неё курсор, нажмите на три точки напротив названия коллекции и в выпадающем списке выберите `Run collection`. В центре экрана появится список запросов коллекции,
а в правой части экрана - меню для настройки параметров запуска.
2. В правом меню включите функцию `Persist responses for a session` - это даст возможность посмотреть ответы API после запуска коллекции.
3. Нажмите кнопку `Run <название коллекции>`.
4. В центре экрана отобразится результат запуска коллекции и тестов. Провалившиеся тесты можно отфильтровать, перейдя во вкладку `Failed`.
Посмотрите детали выполненного запроса и полученного ответа: для этого нажмите на тест.

### Повторный запуск коллекции:

При активированном виртуальном окружении проекта, запустите скрипт для очистки базы данных от объектов, созданных при выполнении запросов коллекции: [`bash clear_db.sh`](https://github.com/Tiaki026/foodgram-project-react/blob/master/backend/clear_db.sh).  
При выполнении скрипта будут удалены все пользователи и объекты, созданные при предыдущем запуске коллекции (при условии корректной настройки параметров `on_delete` в моделях проекта).
  
При сбое очистки базы данных, используйте резервную копию файла `db.sqlite3`: замените текущий файл базы данных на эту копию. 
А можно создать базу данных заново и наполнить её объектами, необходимыми для корректного запуска коллекции (как описано в п.3 раздела _Подготовка Django-проекта к запуску коллекции_).

### Ограничения от разработчиков Postman

В бесплатной версии программы Postman есть техническое ограничение: коллекцию можно беспрепятственно запускать 25 раз в месяц.  
После исчерпания этого лимита Postman не превратится в тыкву: он по-прежнему будет запускать коллекции, но запуск иногда будет блокироваться на 30 секунд (иногда дважды подряд), и в это время в интерфейсе программы будет появляться предложение приобрести платную версию.  
Вы можете купить платную версию, а можете просто продолжить пользоваться бесплатной версией, время от времени прерываясь на просмотр рекламы.

Для отправки отдельных запросов никаких ограничений нет.

# Итог

Проект оказался сложнее, чем думал. Но в большистве сложностей виноват сам я, из-за несвоевременного бекапа кода на гит, из-за усталости, которая вытекает из прошлого пункта, так как приходилось часами настраивать одно и то же. Но все приходит с опытом. Таков путь джуна.

Удачи!

# Автор:
  - [Колотиков Евгений](https://github.com/Tiaki026)