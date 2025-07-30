"""Additional Sphinx directives for the where-next blocks."""

from docutils import nodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util.docutils import SphinxDirective
from sphinx_design.shared import create_component, is_component


class WhereNextDirective(SphinxDirective):
    """The WhereNextDirective directive is used to generate an "Where Next" block."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        where_next = create_component("ou-where-next")
        self.state.nested_parse(self.content, self.content_offset, where_next)
        return [where_next]


class WhereNextHtmlTransform(SphinxPostTransform):
    """Transform where-next containers into the HTML specific AST structures."""

    default_priority = 199
    formats = ("html",)

    def run(self):
        """Run the transform"""
        document: nodes.document = self.document
        for node in document.findall(lambda node: is_component(node, "ou-where-next")):
            newnode = create_component(
                "ou-where-next",
                classes=["ou-where-next"],
            )
            newnode += nodes.raw("", '<p class="ou-where-next-title">Where next?</p>', format="html")
            newnode += node.children
            node.replace_self(newnode)


class WhereNext(nodes.Element):
    def __init__(self, rawsource="", *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)  # noqa: B026
        self.set_class("ou-where-next")


class WhereNextTitle(nodes.Element):
    def __init__(self, rawsource="", *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)  # noqa: B026
        self.set_class("ou-where-next-title")


class WhereNextContent(nodes.Element):
    def __init__(self, rawsource="", *children, **attributes):
        super().__init__(rawsource=rawsource, *children, **attributes)  # noqa: B026
        self.set_class("ou-where-next-content")


def setup(app):
    """Setup the Where Next extensions."""
    app.add_directive("where-next", WhereNextDirective)
    app.add_post_transform(WhereNextHtmlTransform)
