"""Time-related Sphinx directives."""  # noqa: A005

from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from sphinx_design.shared import create_component


class TimeDirective(SphinxDirective):
    """The TimeDirective directive is used to generate a time block."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        time = create_component(
            "ou-time", classes=["ou-time"], children=[nodes.Text(self.arguments[0], self.arguments[0])]
        )
        return [time]


def setup(app):
    """Setup the Time extensions."""
    app.add_directive("time", TimeDirective)
