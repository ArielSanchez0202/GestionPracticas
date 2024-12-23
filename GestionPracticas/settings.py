"""
Django settings for GestionPracticas project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%ob=$u84-wg(+wqs=a4l2e46i^c$@y76u4ukjmh50!f555^ra#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'coordinador',
    'core',
    'estudiante',
    'autenticacion',
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

ROOT_URLCONF = 'GestionPracticas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'coordinador.context_processors.fichas_pendientes',
            ],
        },
    },
]

WSGI_APPLICATION = 'GestionPracticas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'practicas',
        'USER': 'postgres',
        'PASSWORD': '692001',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Ruta para los archivos estáticos en desarrollo
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static", 
    BASE_DIR / "estudiante" / "static",
]

# Directorio donde se recopilarán todos los archivos estáticos cuando se ejecute 'collectstatic'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Esto debería ser un directorio separado

LOGOUT_REDIRECT_URL = 'home'

#Emails
DEFAULT_FROM_EMAIL = "envios@dominio.cl"#agregue un correo que aparecerá en el correo enviado, este no necesariamente debe ser una casilla que exista
EMAIL_HOST = 'smtp.gmail.com' #servidor de salida del proveedor de correo, por lo general se usa smtp.dominio
EMAIL_PORT = 587 #Puerto del servidor de salida, el proveedor de correo debe indicar el puerto que usará
EMAIL_HOST_USER = 'vicente.menaalbornoz@gmail.com'#correo que se usará para el envio, esta casilla debe existir en el servidor
EMAIL_HOST_PASSWORD = 'wpfp vmlv mcam wjjp'#contraseña de acceso del correo usado en el paso anterior
EMAIL_USE_TLS = True #habilita el protocolo de seguridad que cifra los correos

MANIFEST_LOADER = {
    'output_dir': 'core/static/dist/',  # where webpack outputs to, if not 
    'manifest_file': 'manifest.json',  # name of your manifest file
    'cache': False,  # recommended True for production, requires a server restart to pick up new values from the manifest.
    'loader': 'django.template.loaders.filesystem.Loader'  # how the manifest files are interacted with
    }

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Configuración para la duración de la sesión
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Cambia esto a True si deseas que la sesión expire al cerrar el navegador
SESSION_COOKIE_AGE = 1209600  # 2 semanas (ajusta el valor según tus necesidades)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')