import os
import sys


docs_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(docs_dir, "..", ".."))


sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "contacts_api"))

project = "Contacts API"
copyright = "2026, Kiril"
author = "Kiril"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_mock_imports = [
    "fastapi",
    "pydantic",
    "sqlalchemy",
    "passlib",
    "jose",
    "jwt",
    "pydantic_settings",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]