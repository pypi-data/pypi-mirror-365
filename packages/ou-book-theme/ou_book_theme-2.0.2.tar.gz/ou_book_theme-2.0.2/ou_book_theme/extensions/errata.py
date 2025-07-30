"""Additional Sphinx directives for OU errata lists."""

import re

from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from sphinx_design.shared import create_component, is_component


class ErratalistDirective(SphinxDirective):
    """The Erratalist directive is used to generate the list of all errate in the site."""

    def run(self):
        """Generate the basic structure."""
        return [create_component("ou-errata-list", rawtext=self.content)]


class ErratumDirective(SphinxDirective):
    """The ErratumDirective directive is used to generate an individual erratum."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        """Generate the erratum reference target and content."""
        erratum_id = f"erratum-{self.env.new_serialno('erratum')}"
        erratum_target = nodes.target("", "", ids=[erratum_id])

        erratum = create_component(
            "ou-erratum",
            classes=["ou-erratum", "margin"],
            rawtext=self.content,
        )
        content = nodes.admonition("", classes=["erratum"])
        content.children.append(
            nodes.paragraph(self.arguments[0], text=self.arguments[0], classes=["admonition-title"])
        )
        erratum.children.append(content)
        self.state.nested_parse(self.content, self.content_offset, content)

        if not hasattr(self.env, "errata_list"):
            self.env.errata_list = []
        self.env.errata_list.append(
            {
                "docname": self.env.docname,
                "target": erratum_target,
                "title": self.arguments[0],
                "group": self.arguments[0],
                "erratum": content,
            }
        )

        return [erratum_target, erratum]


def purge_doc_errata(app, env, docname):  # noqa: ARG001
    """Purge the environment errata_list for the docname."""
    if hasattr(env, "errata_list"):
        env.errata_list = [erratum for erratum in env.errata_list if erratum["docname"] != docname]


def merge_errata(app, env, docnames, other):  # noqa: ARG001
    """Merge an updated errata_list."""
    if not hasattr(env, "errata_list"):
        env.errata_list = []
    if hasattr(other, "errata_list"):
        env.errata_list.extend(other.errata_list)


def errata_sort_key(erratum):
    """Sort errata titles by group."""
    if re.match(r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4}", erratum["group"]):
        parts = erratum["group"].split(".")
        parts.reverse()
        return [int(part) for part in parts]
    else:
        return [erratum["group"]]


def transform_errata_lists(app, doctree, fromdocname):
    """Transform all ou-errata-list components into nested bulleted lists."""
    for node in doctree.findall(lambda node: is_component(node, "ou-errata-list")):
        errata_list = nodes.bullet_list()

        if hasattr(app.env, "errata_list"):
            app.env.errata_list.sort(key=errata_sort_key)
            app.env.errata_list.reverse()
            last_group = None
            group = None
            for erratum in app.env.errata_list:
                if last_group != erratum["group"]:
                    last_group = erratum["group"]
                    group_item = nodes.list_item()
                    group_para = nodes.paragraph()
                    group_para.append(nodes.strong(last_group, last_group))
                    group_item.append(group_para)
                    group = nodes.bullet_list()
                    group_item.append(group)
                    errata_list.append(group_item)
                erratum_node = nodes.reference("", "")
                erratum_node["refdocname"] = erratum["docname"]
                erratum_node["refuri"] = (
                    f"{app.builder.get_relative_uri(fromdocname, erratum['docname'])}#{erratum['target']['refid']}"
                )
                erratum_node["internal"] = True
                erratum_node.extend(app.env.titles[erratum["docname"]].children)

                para = nodes.paragraph()
                para.append(erratum_node)
                list_item = nodes.list_item()
                list_item.append(para)
                list_item.extend(erratum["erratum"].children[1:])
                group.append(list_item)
        else:
            para = nodes.paragraph("No errata have been published.", "No errata have been published.")
            list_item = nodes.list_item()
            list_item.append(para)
            errata_list.append(list_item)

        node.replace_self(errata_list)


def setup(app):
    """Setup the Errata extensions."""
    app.add_directive("errata-list", ErratalistDirective)
    app.add_directive("erratum", ErratumDirective)
    app.connect("doctree-resolved", transform_errata_lists)
    app.connect("env-purge-doc", purge_doc_errata)
    app.connect("env-merge-info", merge_errata)
