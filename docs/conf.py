"""Sphinx configuration."""

project = "Whenwasi"
author = "Andrew Schweitzer"
copyright = "2022, Andrew Schweitzer"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
