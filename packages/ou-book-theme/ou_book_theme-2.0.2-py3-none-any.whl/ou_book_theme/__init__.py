# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The main OU Book Theme entry point."""

from os import path
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset, copy_asset_file
from sphinx_book_theme import hash_assets_for_files

from ou_book_theme import extensions


def get_html_theme_path():
    """Return list of HTML theme paths."""
    parent = Path(__file__).parent.resolve()
    theme_path = parent / "theme" / "ou_book_theme"
    return theme_path


def hash_js_css_assets(app, pagename, templatename, context, doctree):  # noqa: ARG001
    """Add hashed CSS and JS assets."""
    assets = ["styles/ou-book-theme.css", "scripts/ou-book-theme.js"]
    hash_assets_for_files(assets, get_html_theme_path() / "static", context, app)


def copy_custom_files(app, exc):
    """Copy custom logo and favicon files."""
    if app.builder.format == "html" and not exc:
        staticdir = path.join(app.builder.outdir, "_static")
        ouheadersdir = path.join(app.builder.outdir, "ouheaders")
        copy_asset_file(str(get_html_theme_path() / "static/images/favicon.svg"), staticdir)
        copy_asset(str(get_html_theme_path() / "ouheaders"), ouheadersdir)


def setup(app: Sphinx):
    """Set up the theme and its extensions."""
    # Register theme
    theme_dir = get_html_theme_path()
    app.add_html_theme("ou_book_theme", theme_dir)
    app.add_js_file("scripts/ou-book-theme.js")

    app.connect("html-page-context", hash_js_css_assets)
    app.connect("build-finished", copy_custom_files)

    extensions.setup(app)

    return {"parallel_read_safe": True, "parallel_write_safe": True}
