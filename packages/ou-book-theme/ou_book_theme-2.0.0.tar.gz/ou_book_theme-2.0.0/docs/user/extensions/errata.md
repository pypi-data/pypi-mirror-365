# Errata

The `{errata-list}` and `{erratum}` blocks are used to simplify adding errata to the site.

## List of errata

The list of errata is generated using the `{errata-list}` block. This is an empty block and all its content will be
automatically generated based on the `{erratum}` blocks used in the project:

::::{code-block} markdown
:::{errata-list}
:::
::::

:::{errata-list}
:::

## Single erratum

The `{erratum}` block generates a single erratum and automatically adds it to any `{errata-list}` blocks across the
site. The `{erratum}` **must** have a title and some content:

::::{code-block} markdown
:::{erratum} 20.02.2025
Something went wrong here.
:::

:::{erratum} 25.02.2025
Something went wrong here.
:::
::::

:::{erratum} 20.02.2025
Something went wrong here.
:::

:::{erratum} 25.02.2025
Something went wrong again.
:::
