SECRET_KEY = 1

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "strawberry.django",
    "tests.app",
]
ROOT_URLCONF = "tests.app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
    },
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
