"""
Django settings for troca project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
# from django.contrib.comments.models import Comment # old

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6-ap3p=akg#9_3e_qei0-&h#jxvgsi=k*(!lzrz$n3z91eglx3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

ALLOWED_HOSTS = ['.troca.ml', '.troca.cc']

SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)
LOGIN_URL = '/login/'

# Application definition

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	#other
	'core',
	'registration',
	'crispy_forms',
	'crispy_forms_foundation',
	'ajax_select',
	#'postman',
	'pure_pagination',
	'froala_editor',
	'phileo',
	'django_social_share',
	'django_messages',
	'feedback_form',
	'sanitizer',
	'django.contrib.humanize',
# 	 'threadedcomments',
#     'django_comments',
#     'django.contrib.sites',
)

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# COMMENTS_APP = 'threadedcomments'

AUTHENTICATION_BACKENDS = ('phileo.auth_backends.CanLikeBackend',)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'comunlaboratorio@gmail.com'
EMAIL_HOST_USER = 'comunlaboratorio@gmail.com'
EMAIL_HOST_PASSWORD = 'comunlab2014'

PHILEO_LIKABLE_MODELS = {
	'troca.Project': {},  # can override default config settings for each model here
	'troca.UserProfile': {},
	'troca.Comment': {},
}

ROOT_URLCONF = 'troca.urls'

WSGI_APPLICATION = 'troca.wsgi.application'


#AJAX_LOOKUP_CHANNELS = {
#    'postman_users': dict(model='auth.user', search_field='username'),
#}

POSTMAN_DISALLOW_ANONYMOUS = True  # default is False
POSTMAN_AUTO_MODERATE_AS = True
POSTMAN_DISABLE_USER_EMAILING = False  # default is False
POSTMAN_NOTIFIER_APP = None  # default is 'notification'
POSTMAN_MAILER_APP = 'django.core.mail.backends.smtp.EmailBackend'  # default is 'mailer'
POSTMAN_AUTOCOMPLETER_APP = {
	 'name': '',  # default is 'ajax_select'
	 'field': 'AutoCompleteField',  # default is 'AutoCompleteField'
	 'arg_name': 'channel',  # default is 'channel'
	 'arg_default': 'postman_users',  # no default, mandatory to enable the feature
 }

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}

TEMPLATE_CONTEXT_PROCESSORS += (
	'django.core.context_processors.request',
	'django_messages.context_processors.inbox',
)


PAGINATION_SETTINGS = {
	'PAGE_RANGE_DISPLAYED': 9,
	'MARGIN_PAGES_DISPLAYED': 2,
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATIC_URL = "/static/"




TEMPLATE_DIRS = (
	PROJECT_PATH + '/templates/',
)

MEDIA_ROOT= os.path.join(PROJECT_PATH, 'media')
MEDIA_URL='/media/'
FROALA_UPLOAD_PATH='/media/uploads/froala_editor/images/'
#Template context processors

("django.contrib.auth.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"django.core.context_processors.static",
"django.core.context_processors.tz",
"django.contrib.messages.context_processors.messages",
"postman.context_processors.inbox")

#Forms template

SANITIZER_ALLOWED_TAGS = ['a', 'p', 'img', 'strong', 'em', 'u', 'blockquote', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
SANITIZER_ALLOWED_ATTRIBUTES = ['href', 'src']

CRISPY_TEMPLATE_PACK = 'foundation-5'

('django.contrib.auth.backends.ModelBackend',)
