# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import tomllib

# Workaround for https://github.com/sphinx-toolbox/sphinx-toolbox/issues/190
# taken from https://github.com/canonical/imagecraft/pull/181/commits/d8bab5d434759bac17861ae3529e55e1a84c2ef5
import sphinx_prompt  # type: ignore[import-not-found]

sys.modules["sphinx-prompt"] = sphinx_prompt

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../../src"))

import rogue_scroll  # noqa

from rogue_scroll import __about__  # noqa

# Pull general sphinx project info from pyproject.toml
# Modified from https://stackoverflow.com/a/75396624/1304076
with open("../../pyproject.toml", "rb") as f:
    toml = tomllib.load(f)

pyproject = toml["project"]

project = pyproject["name"]
release = __about__.__version__
author = ",".join([author["name"] for author in pyproject["authors"]])
copyright = __about__.__copyright__

github_username = "jpgoldberg"
github_repository = "rogue-scroll"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "sphinx.ext.doctest",
    "sphinx_toolbox.more_autodoc.augment_defaults",
    "sphinx.ext.autodoc",
    "sphinx_toolbox.github",
    "sphinx_toolbox.wikipedia",
    "sphinx_toolbox.installation",
    #   "sphinx_toolbox.more_autodoc",
    "sphinx_autodoc_typehints",
    "sphinx_toolbox.more_autodoc.variables",
    "sphinxarg.ext",
]

autodoc_typehints = "both"
typehints_use_signature = True
typehints_use_signature_return = True
always_document_param_types = True
typehints_defaults = "comma"

templates_path = ["_templates"]
exclude_patterns: list[str] = []

rst_prolog = f"""
.. |project| replace:: **{project}**
.. |root| replace:: :mod:`rogue_scroll`
.. |cmd| replace:: ``rogue-scroll``
.. |version| replace:: {release}
.. _rogue: https://en.wikipedia.org/wiki/Rogue_(video_game)
"""
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "nature"
html_static_path = ["_static"]
