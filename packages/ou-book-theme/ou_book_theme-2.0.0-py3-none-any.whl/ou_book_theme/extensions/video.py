"""Additional Sphinx directives for OU OCL Videos."""

import urllib3
import webvtt
from docutils import nodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx_design.shared import create_component, is_component

logger = logging.getLogger(__name__)


class VideoDirective(SphinxDirective):
    """The VideoDirective directive is used to generate video block for videos."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    def run(self):
        if self.arguments[0].startswith("https://video.ocl.open.ac.uk/ui/#/embed/"):
            video_id = self.arguments[0][40:]
            response = urllib3.request("GET", f"https://video.ocl.open.ac.uk/api/videos/{video_id}")
            if response.status == 200:  # noqa: PLR2004
                video = create_component("ou-video", rawtext=self.content, video_id=video_id)
                video += nodes.paragraph(
                    response.json()["title"],
                    response.json()["title"],
                    classes=["admonition-title"],
                )
                cdn_base_url = f"https://video-cdn.ocl.open.ac.uk/videos/{'/'.join(video_id)}/"
                response = urllib3.request("GET", f"{cdn_base_url}transcript.vtt")
                if response.status == 200:  # noqa: PLR2004
                    transcript = create_component(
                        "dropdown",
                        opened=False,
                        type="dropdown",
                        has_title=True,
                        icon="note",
                        chevron=True,
                        container_classes=["sd-mb-3", "ou-transcript"],
                        title_classes=[],
                        body_classes=[],
                    )
                    transcript += nodes.paragraph("Transcript", "Transcript")
                    buffer = []
                    for caption in webvtt.from_string(response.data.decode()):
                        buffer.append(caption.text.strip())
                        if caption.text.strip().endswith(".") and len(buffer) > 0:
                            transcript += nodes.paragraph(" ".join(buffer), " ".join(buffer))
                            buffer = []
                    if len(buffer) > 0:
                        video += nodes.paragraph(" ".join(buffer), " ".join(buffer))
                    video += transcript
                return [video]
            else:
                logger.error(f"OCL Video {video_id} not found")
        return []


class VideoHtmlTransform(SphinxPostTransform):
    """Transform video containers into the HTML specific AST structures."""

    default_priority = 198
    formats = ("html",)

    def run(self):
        """Run the transform"""
        document: nodes.document = self.document
        for node in document.findall(lambda node: is_component(node, "ou-video")):
            video_id = node["video_id"]
            newnode = create_component(
                "ou-video",
                classes=["admonition ou-video"],
            )
            newnode += node.children[0]
            newnode += nodes.raw(
                "",
                f'<iframe src="https://video.ocl.open.ac.uk/ui/#/embed/{video_id}" allow="fullscreen"></iframe>',
                format="html",
            )
            newnode += node.children[1:]
            node.replace_self(newnode)


class VideoLatexTransform(SphinxPostTransform):
    """Transform video containers into the LaTeX specific AST structures."""

    default_priority = 198
    formats = ("latex",)

    def run(self):
        """Run the transform"""
        document: nodes.document = self.document
        for node in document.findall(lambda node: is_component(node, "ou-video")):
            video_id = node["video_id"]
            newnode = create_component(
                "ou-video",
                classes=["admonition ou-video"],
            )
            video_title = nodes.paragraph()
            video_title += nodes.raw("", "\\textbf{Video: ", format="latex")
            video_title += node.children[0].children
            video_title += nodes.raw("", "}", format="latex")
            newnode.append(video_title)
            video_link_para = nodes.paragraph()
            video_link_para += nodes.Text("You can view this video at: ")
            video_link_para += nodes.reference(
                "",
                f"https://video.ocl.open.ac.uk/ui/#/embed/{video_id}",
                refuri=f"https://video.ocl.open.ac.uk/ui/#/embed/{video_id}",
            )
            newnode += video_link_para
            transcript_para = nodes.paragraph()
            transcript_para += nodes.raw("", "\\textbf{Transcript}", format="latex")
            newnode += transcript_para
            newnode += node.children[1].children[1:]
            newnode += nodes.raw("", "\\textcolor[RGB]{220,220,220}{\\rule{\\linewidth}{0.2pt}}", format="latex")
            node.replace_self(newnode)


def setup(app):
    """Setup the Activity extensions."""
    app.add_directive("video", VideoDirective)
    app.add_post_transform(VideoHtmlTransform)
    app.add_post_transform(VideoLatexTransform)
