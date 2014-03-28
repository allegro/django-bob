# configuration only for tests

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'ralph_test',
        'OPTIONS': dict(
        ),
    },
}

SECRET_KEY = "secret"
