project = "OU Book Theme"
root_doc = "index"
extensions = ["myst_parser", "ou_book_theme", "sphinx_external_toc", "sphinxcontrib.mermaid"]
language = "en"
project_copyright = "2023-%Y"

numfig = True

html_title = "OU Book Theme"
html_theme = "ou_book_theme"

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
