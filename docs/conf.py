"""Sphinx configuration for llama-index-pydocker."""

# -- Project information -----------------------------------------------------

project = "llama-index-pydocker"
author = "Amadou Wolfgang Cisse"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# sphinx.ext.autodoc  — generates API reference from docstrings
# sphinx.ext.napoleon — parses NumPy/Google-style docstrings
# sphinx.ext.intersphinx — cross-links to Python stdlib and llama-index-core docs
# sphinx.ext.viewcode — adds [source] links next to each API entry
# myst_parser         — allows all doc files to be written in Markdown
# nbsphinx            — renders usage/*.ipynb notebooks in the docs

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_parser",
    "nbsphinx",
]

# MyST: recognise .md as source files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Paths relative to this conf.py file
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# Suppress warnings that originate outside our docs:
# myst.xref_missing — .ipynb links are file links, not Sphinx cross-refs
# toc.not_readable  — notebooks live in usage/ (outside the docs source dir)
# docutils          — **kwargs patterns in source docstrings parsed as RST bold
suppress_warnings = ["myst.xref_missing", "toc.not_readable", "docutils"]

# -- Intersphinx mapping -----------------------------------------------------
# python      — link to stdlib symbols from docstrings
# llama_index — link to upstream store base classes

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    # llama-index does not publish a Sphinx objects.inv — omitted
}

# -- Autodoc -----------------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# -- Napoleon ----------------------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- nbsphinx ----------------------------------------------------------------
# Do not execute notebooks during the docs build; use pre-executed outputs.

nbsphinx_execute = "never"

# -- HTML output -------------------------------------------------------------
# furo: clean, responsive, dark-mode ready; used by pip, pipx, black.
# No JavaScript dependencies. Sidebar shows the full toctree by default.

html_theme = "furo"
html_title = "llama-index-pydocker"

html_theme_options = {
    "sidebar_hide_name": False,
}
