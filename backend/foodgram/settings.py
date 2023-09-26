# flake8: noqa
import os
from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', default='123no_key321asf5674r84g5f6h4t84h2gj46tj423')
# SECRET_KEY = 'django-insecure-o9#6w)8v%9xf4eb%skywm+(ny^j%t^q*w&e#5y8xj+66!zm)i4'
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', default='127.0.0.1').split(',')

DEBUG = os.getenv('DEBUG')
# DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'api.apps.ApiConfig',
    'users.apps.UsersConfig',
    'recipes.apps.RecipesConfig',
    'rest_framework',
    'djoser',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv("DB_ENGINE", default='django.db.backends.postgresql'),
            'NAME': os.getenv('POSTGRES_DB', default='default_db'),
            'USER': os.getenv('POSTGRES_USER', default='default_user'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='default_password'),
            'HOST': os.getenv('DB_HOST', default='default_host'),
            'PORT': os.getenv('DB_PORT', default='5432')
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.CustomUser'

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = 'static/'
# STATIC_ROOT = BASE_DIR / STATIC_URL
STATIC_ROOT = BASE_DIR / STATIC_URL

MEDIA_URL = 'media/'
# MEDIA_ROOT = BASE_DIR / MEDIA_URL
MEDIA_ROOT = BASE_DIR / MEDIA_URL

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 6

}

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'api.serializers.CreateCustomUserSerializer',
        'user': 'api.serializers.CustomUserSerializer',
        'user_list': 'api.serializers.CustomUserSerializer',
        'current_user': 'api.serializers.CustomUserSerializer',
    },

    'PERMISSIONS': {
        'user': ['djoser.permissions.CurrentUserOrAdminOrReadOnly'],
        'user_list': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
        # 'user_list': ['api.permissions.IsAdminOrOwnerOrReadOnly'],
        # 'resipe': ['api.permissions.IsAdminOrOwnerOrReadOnly'],
        # 'recipe_list': ['api.permissions.IsAdminOrOwnerOrReadOnly'],
    },

    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
}