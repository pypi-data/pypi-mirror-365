# Figures

As well as embedding images using `{Figure}` directives, images can also be generated using the []`mermaid.js`](https://mermaid.js.org/) diagramming tool.

The generated image is saved as a `.png` file and automatically linked to.

Diagram scripts may be specified using the `{mermaid}` directive:

````text
```{mermaid}
:alt: 
:caption: Publishing workflows from MyST markdown

flowchart LR
  A[Jupyter Notebook] --> C
  B[MyST Markdown] --> C
  C(mystmd) --> D{"Sphinx\n+\npandoc"}
  D --> E[LaTeX]
  E --> F[PDF]
  D --> G[Word]
  D --> H[XML] --> I[OU-XML]
  D --> J[HTML]
  I --> K[OU-VLE]
  I --> L[OU-PDF]
```
````

```{mermaid}
:alt: 
:caption: Publishing workflows from MyST markdown

flowchart LR
  A[Jupyter Notebook] --> C
  B[MyST Markdown] --> C
  C(mystmd) --> D{"Sphinx\n+\npandoc"}
  D --> E[LaTeX]
  E --> F[PDF]
  D --> G[Word]
  D --> H[XML] --> I[OU-XML]
  D --> J[HTML]
  I --> K[OU-VLE]
  I --> L[OU-PDF]
```

Diagram scripts can also be included in a markdown file using colon fenced blocks:

```text
:::{mermaid}
:alt:
:caption: A class diagram showing the Module, JupyterBook, and Theme. The Module is linked to the JupyterBook, which in turn is linked to the Theme
ClassDiagram
  Module -- JupyterBook -- Theme
:::
```

:::{mermaid}
:alt:
:caption: A class diagram showing the Module, JupyterBook, and Theme. The Module is linked to the JupyterBook, which in turn is linked to the Theme
ClassDiagram
  Module -- JupyterBook -- Theme
:::
