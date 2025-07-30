# Installation

To use the OU Book Theme, first install it into your project:

:::{code-block} console
$ pip install ou-book-theme
:::

Then enable the theme in your {file}`_config.yml`:

:::{code-block} yaml
sphinx:
  extra_extensions:
    - ou_book_theme
  config:
    html_theme: ou_book_theme
:::

Next, create a {file}`_static` directory and add an empty {file}`favicon.svg` file. This will automatically be
overwritten by the theme, but needs to be in place for the build process to know that the files exist.

Then set the necessary settings in the `sphinx.config.html_theme_options.logo` and `html.favicon` keys in the
{file}`_config.yml`:

:::{code-block} yaml
sphinx:
  config:
    html_theme_options:
      logo:
        image_light: "_static/logo-light.svg"
        image_dark: "_static/logo-dark.svg"

...

html:
  favicon: _static/favicon.svg
:::

You are now ready to build your book with the OU Book Theme.
