"""JupyterBook CLI extension."""

import os
from typing import Annotated

from livereload import Server, shell
from typer import Argument, Option, Typer

cli = Typer()


@cli.command()
def build(path: Annotated[str, Argument(help="Path to the OU book")]) -> None:
    """Serve the OU Book locally."""
    full_build = shell(f"sphinx-build --builder html --fresh-env docs {os.path.join(path, '_build', 'html')}")
    full_build()


@cli.command()
def serve(
    path: Annotated[str, Argument(help="Path to the OU book")],
    host: Annotated[str, Option(help="The host to serve the book at")] = "127.0.0.1",
    port: Annotated[int, Option(help="The port to serve the book at")] = 8000,
) -> None:
    """Serve the OU Book locally."""
    partial_build = shell(f"sphinx-build --builder html {path} {os.path.join(path, '_build', 'html')}")
    full_build = shell(f"sphinx-build --builder html --fresh-env docs {os.path.join(path, '_build', 'html')}")
    full_build()

    server = Server()
    server.watch(f"{path}/**/*.md", partial_build)
    server.watch(f"{path}/**/*.yml", full_build)
    server.watch(f"{path}/**/*.py", full_build)
    server.watch(f"{path}/**/*.png", full_build)
    server.watch(f"{path}/**/*.jpg", full_build)
    server.watch(f"{path}/**/*.jpeg", full_build)
    server.watch(f"{path}/**/*.svg", full_build)
    server.serve(root=f"{path}/_build/html", port=port, host=host)
