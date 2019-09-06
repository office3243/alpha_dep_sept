import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '+qkf6u0n7@xpqt#0_c61pmacz)tk%rgv*65m!-mrb%5s8#ga_c'

DEBUG = True

ALLOWED_HOSTS = ["*", ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',

    "accounts",
    "orders",
    "products",
    "portal",
    "carts_app",
    "django_filters",
    "payments",
    "enquiries",
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

ROOT_URLCONF = 'alphahub_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'alphahub_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static/")

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

#   CUSTOM SETTINGS
AUTH_USER_MODEL = 'accounts.User'
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"
SITE_DOMAIN = "http://127.0.0.1:8000"


#   PAYTM TEST
PAYTM_MERCHANT_KEY = "mhTAUyOuhW752G_q"
PAYTM_MERCHANT_ID = "VgBKhn41304614600778"
PAYTM_WEBSITE = 'DEFAULT'
PAYTM_CALLBACK_URL = SITE_DOMAIN + "/payments/paytm/response/"


API_KEY_2FA = "c9ef2a2e-806a-11e9-ade6-0200cd936042"

CRISPY_TEMPLATE_PACK = "bootstrap4"


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'webalphahub@gmail.com'
EMAIL_HOST_PASSWORD = 'Abdul1996@'

EMAIL_FROM = EMAIL_HOST_USER
ADMIN_EMAIL = "alphahub27@gmail.com"
