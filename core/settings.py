from django.core.exceptions import ImproperlyConfigured
from decouple import config
from logging import config
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gbrng&khmt)48ht5+b40%p*h#n0j2r-7jp9=2+%(jj$no0x049'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'deboutwanindara.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]


# Application definition


CUSTOM_APPS = [
    'home',
    'contact',
    'action',
    'join',
    'blog'
]

EXTERNAL_APPS = [
    
]

DJANGO_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core'
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + CUSTOM_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static'),
]

# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# CONFIGURATION EMAIL INTELLIGENTE - FONCTIONNE EN DEV ET PROD
# ==============================================================================


from decouple import config

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_TIMEOUT = 30

DEFAULT_FROM_EMAIL = f"Debout Wanindara <{EMAIL_HOST_USER}>"

# ==============================================================================
# CONFIGURATION LANGUES
# ==============================================================================
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('fr', _('Français')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'fr'

USE_I18N = True

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Activation de la localisation
USE_L10N = True

# Fuseau horaire
TIME_ZONE = 'Africa/Conakry'  # Ajustez selon votre localisation
USE_TZ = True

# Jazzmin configuration
JAZZMIN_SETTINGS = {
    "site_title": "Administration - Debout Wanindara",
    "site_header": "Debout Wanindara",
    "site_brand": "Debout Wanindara",
    "site_logo": "img/logo.png",
    "site_logo_classes": "img-circle shadow-sm",
    "site_icon": "img/favicon.png",
    "welcome_sign": "Bienvenue dans l'administration de Debout Wanindara",
    "copyright": "© Debout Wanindara",
    
    # TOP MENU - Simplifiez-le
    "topmenu_links": [
        {"name": "Accueil", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Voir le site", "url": "https://deboutwanindara.pythonanywhere.com", "new_window": True},
    ],
    
    # USER MENU
    "usermenu_links": [
        {"model": "auth.user"}
    ],
    
    # SIDEBAR CONFIGURATION
    "show_sidebar": True,
    "navigation_expanded": False,  # CHANGEZ À False POUR RÉDUIRE LE DÉBORDEMENT
    "hide_apps": [],  # Apps à cacher si nécessaire
    "hide_models": [],  # Modèles à cacher
    
    # ICONS
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "home": "fas fa-home",  # Ajoutez vos apps ici
        "contact": "fas fa-envelope",
        "action": "fas fa-hands-helping",
        "join": "fas fa-user-plus",
        "blog": "fas fa-blog",
    },
    
    # DEFAULTS
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # CSS PERSONNALISÉ - CRÉEZ CE FICHIER
    "custom_css": "css/admin_custom.css",
    "custom_js": None,
    
    # GOOGLE FONTS
    "use_google_fonts_cdn": True,
    
    # FORMAT DES FORMULAIRES
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    
    # CHOIX DE LANGUE
    "language_chooser": True,
    
    # RESPONSIVE
    "sidebar_width": "230px",  # Réduisez la largeur
    
    # THÈME - Essayez un thème plus léger
    "theme": "default",  # Ou "flatly", "cosmo"
    
    # DARK MODE
    "theme_dark": False,
    
    # BOUTONS D'ACTION
    "actions_sticky_top": True,
}
