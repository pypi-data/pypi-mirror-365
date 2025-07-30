# Markup

The Jupyter Book setup uses MyST Markdown as the markup language for writing content and provides a wide range of markup functionality, which is documented in detail [here](https://jupyterbook.org/en/stable/content/index.html).

## Numbering and referencing figures

When figure captions are generated, the caption will, by default, be prefixed with an automatically generated figure number taking the form *Figure 1 Caption text*.

Figure reference numbers may also be generated with a section number prefix, for example *Figure 1.1 Caption text*. Specify which figure numbering approch to use via the `_config.yml` file:

- `sphinx.config.numfig_secnum_depth: 0`: incremental count over all figures (e.g. *Figure 1*)
- `sphinx.config.numfig_secnum_depth: 1`: incremental figure count within a section (e.g. *Figure 1.1*).

If the `_config.yml` file includes the setting `sphinx.config.numfig: true`, figures may be referenced from markdown text using the construction:

::::{code-block} markdown
Make a figure reference from the text, see {numref}`figure_ref`.

:::{figure} path/image.png
:name: figure_ref

Caption text

Longer description text.
:::
::::

The format used for the reference text may be configured via the `sphinx.config.numfig_format` setting; for example, `numfig_format: {'figure':'Figure %s'}`.

By default, Sphinx will generate inline reference numbers that include the session number, rather than using the simple incremental count over all figures. To guarantee that the inline figure reference style matches the figure reference style in the figure caption, you should explicitly set `sphinx.config.numfig_secnum_depth` in the `_config.yml` file.
