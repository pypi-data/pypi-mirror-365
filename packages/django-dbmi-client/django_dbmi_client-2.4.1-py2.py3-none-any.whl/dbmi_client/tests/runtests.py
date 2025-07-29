#!/usr/bin/env python
"""
This script is a trick to setup a fake Django environment, since this reusable
app will be developed and tested outside any specifiv Django project.
Via ``settings.configure`` you will be able to set all necessary settings
for your app and run the tests as if you were calling ``./manage.py test``.
"""
import sys
import pytest
from django.conf import settings

EXTERNAL_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
]
INTERNAL_APPS = [
    "dbmi_client",
]
INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

if not settings.configured:
    settings.configure(
        SECRET_KEY="*4n1!z0%@w-e&u9c-kpyqof=-nxvx^v2m000#gf9vewm3s+_v)",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=INSTALLED_APPS,
        DBMI_CLIENT_CONFIG={
            "CLIENT": "DBMI-Client",
            "ENVIRONMENT": "prod",
            "AUTH_CLIENTS": {"someauthclientid":{"JWKS_URL":"https://somejwksurl.com/","PROVIDER":"cognito"}},
        },
    )


def main(*test_args):
    sys.exit(pytest.main(["-x"]))


if __name__ == "__main__":
    main(*sys.argv[1:])
