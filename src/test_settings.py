from settings import *

DEBUG = False
CACHEOPS_ENABLED = False

REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = "json"

LOGGING = {}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

CELERY_TASK_ALWAYS_EAGER = True


LOG_APPS = ()

