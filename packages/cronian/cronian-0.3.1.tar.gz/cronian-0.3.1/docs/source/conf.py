# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'cronian'
copyright = '2025, Christian Doh Dinga, Sander van Rijn, Flavio Hafner'
author = 'Christian Doh Dinga, Sander van Rijn, Flavio Hafner'
release = '0.3.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autoapi.extension',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx_copybutton',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = []

autoapi_dirs = ['../../src']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
