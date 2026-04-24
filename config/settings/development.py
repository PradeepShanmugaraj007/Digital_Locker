"""Development settings."""
from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all hosts in dev
ALLOWED_HOSTS = ["*"]

# Django Debug Toolbar (optional install)
INSTALLED_APPS += ["django.contrib.admindocs"]  # noqa: F405

# Use file + console logging in dev; Logstash optional
