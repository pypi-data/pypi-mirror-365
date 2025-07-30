# Extensions

The OU Book Theme provides a number of markup extensions for OU-specific functionality:

:::{tableofcontents}
:::

It also automatically installs the following Sphinx extensions, which can then be enabled as needed:

* **[Mermaid](https://sphinxcontrib-mermaid-demo.readthedocs.io)**: for generating diagrams using [Mermaid](https://mermaid.js.org/).

  To enable Mermaid diagrams you need to enable the extension in the {file}`_config.yml`:

  :::yaml
  sphinx:
    extra_extensions:
      - sphinxcontrib.mermaid
  :::
