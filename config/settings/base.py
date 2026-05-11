from pathlib import Path
from django.urls import reverse_lazy
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

DJANGO_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

THIRD_PARTY_APPS = [
    "imagekit",
    "django_apscheduler",
    "meta",
]

LOCAL_APPS = [
    "apps.core",
    "apps.seo",
    "apps.media_manager",
    "apps.blog",
    "apps.pages",
    "apps.services",
    "apps.ai_assistant",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# DATABASES se define en development.py (SQLite) y production.py (PostgreSQL)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache usando la base de datos (sin Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    }
}

# django-apscheduler
APSCHEDULER_DATETIME_FORMAT = "d/m/Y H:i:s"
APSCHEDULER_RUN_NOW_TIMEOUT = 25

# DigitalOcean AI Platform (Gradient)
DO_MODEL_ACCESS_KEY = config("DO_MODEL_ACCESS_KEY", default="")

# django-meta (SEO)
META_SITE_PROTOCOL = "https"
META_SITE_DOMAIN = "www.loginco.com.mx"
META_SITE_NAME = "Loginco Corp"
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_GOOGLEPLUS_PROPERTIES = False
META_DEFAULT_KEYWORDS = ["agencia aduanal", "logística", "transporte", "bodega", "loginco"]
META_INCLUDE_KEYWORDS_TAG = True

# Email — SendGrid SMTP relay
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"  # SendGrid siempre usa la cadena literal "apikey"
EMAIL_HOST_PASSWORD = config("SENDGRID_API_KEY", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@loginco.com.mx")
CONTACT_EMAIL = config("CONTACT_EMAIL", default="contacto@loginco.com.mx")

# Unfold Admin
UNFOLD = {
    "SITE_TITLE": "Loginco Corp",
    "SITE_HEADER": "Loginco Corp",
    "SITE_URL": "/",
    "SITE_SYMBOL": "language",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "BORDER_RADIUS": "6px",
    "COLORS": {
        "base": {
            "50":  "249 250 251",
            "100": "243 244 246",
            "200": "229 231 235",
            "300": "209 213 219",
            "400": "156 163 175",
            "500": "107 114 128",
            "600": "75 85 99",
            "700": "55 65 81",
            "800": "31 41 55",
            "900": "17 24 39",
            "950": "3 7 18",
        },
        "primary": {
            "50":  "240 249 255",
            "100": "224 242 254",
            "200": "186 230 253",
            "300": "125 211 252",
            "400": "56 189 248",
            "500": "14 165 233",
            "600": "2 132 199",
            "700": "3 105 161",
            "800": "7 89 133",
            "900": "12 74 110",
            "950": "8 47 73",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Contenido",
                "separator": True,
                "items": [
                    {
                        "title": "Publicaciones",
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_post_changelist"),
                    },
                    {
                        "title": "Categorías",
                        "icon": "category",
                        "link": reverse_lazy("admin:blog_category_changelist"),
                    },
                    {
                        "title": "Etiquetas",
                        "icon": "label",
                        "link": reverse_lazy("admin:blog_tag_changelist"),
                    },
                    {
                        "title": "Sitios destino",
                        "icon": "language",
                        "link": reverse_lazy("admin:blog_sitetarget_changelist"),
                    },
                ],
            },
            {
                "title": "Media",
                "separator": True,
                "items": [
                    {
                        "title": "Archivos",
                        "icon": "photo_library",
                        "link": reverse_lazy("admin:media_manager_mediafile_changelist"),
                    },
                ],
            },
            {
                "title": "Sistema",
                "separator": True,
                "items": [
                    {
                        "title": "Usuarios",
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Tareas programadas",
                        "icon": "schedule",
                        "link": reverse_lazy("admin:django_apscheduler_djangojob_changelist"),
                    },
                    {
                        "title": "Generaciones IA",
                        "icon": "psychology",
                        "link": reverse_lazy("admin:ai_assistant_aigenerationlog_changelist"),
                    },
                ],
            },
        ],
    },
}
