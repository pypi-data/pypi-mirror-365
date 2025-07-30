# Command-line

The OU Book Theme provides an Command-line interface (CLI). To run
the CLI commands use:

:::{code-block} shell
$ obt
:::

The following additional CLI commands are available:

## build - Build the book

Use the `build` command to create the HTML files:

:::{code-block} shell
$ obt build {PATH}
:::

The built HTML files are then in {filename}`{PATH}/_build/html`.

## serve - Run a local development server

Use the `serve` command to run a local development server:

:::{code-block} shell
$ obt serve {PATH}
:::

The book is then available at http://localhost:8000.

When you make changes to the book content, the book is automatically rebuilt and the web-page reloaded.
Depending on the size of the book, this may take a few seconds. Check the terminal for any errors.

You can configure the host and port to make the book available at by providing the `--host {IP_OR_HOSTNAME}`
and / or `--port {PORT}` options to the `serve` command.
