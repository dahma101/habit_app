"""Sphinx configuration for Habit Tracker API documentation."""

import os
import sys
import django

sys.path.insert(0, os.path.abspath(".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

project = "Habit Tracker"
copyright = "2026, Habit Tracker"
author = "Habit Tracker Team"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinxcontrib_django",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
