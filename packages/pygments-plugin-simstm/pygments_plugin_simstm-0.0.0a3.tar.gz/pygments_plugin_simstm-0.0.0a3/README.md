# SimStm Pygments Lexer Plugin

A Pygments plugin that provides syntax highlighting support for the [SimStm language](https://github.com/eccelerators/simstm).  
SimStm is a small, stack-based language used for defining simulation control flows.

This plugin adds a custom lexer so that `.stm` files can be syntax-highlighted in Pygments-supported tools (e.g., Sphinx, code formatters, converters, etc.).

---

## General

- **Project Name:** SimStm Pygments Lexer
- **Language Supported:** [SimStm](https://github.com/eccelerators/simstm)
- **Lexer Type:** Pygments plugin
- **License:** MIT

This project is useful for:
- Rendering `.stm` files with syntax highlighting in HTML, LaTeX, or terminal output using [Pygments](https://pygments.org/)
- Integrating SimStm support in Sphinx documentation
- Editor plugin integrations that use Pygments lexers

---

## Installation (for users)

You can install the lexer directly from PyPI:

```bash
pip install simstm-pygments-lexer
```

### Usage with `pygmentize`

```bash
pygmentize -f html -o output.html yourfile.stm
```

Or with style options:

```bash
pygmentize -f html -O full,style=monokai -o out.html yourfile.stm
```

---

## Usage in Sphinx

To enable SimStm highlighting in [Sphinx](https://www.sphinx-doc.org/):

1. Add `simstm-pygments-lexer` to your project's `requirements.txt`
2. Use `.. code-block:: simstm` or `.. highlight:: simstm` in your `.rst` or `.md` docs

---

## Development Setup

### Clone the project

```bash
git clone https://github.com/YOUR_USERNAME/simstm-pygments-lexer.git
cd simstm-pygments-lexer
```

### Set up environment with Hatch

Make sure [Hatch](https://hatch.pypa.io/) is installed:

```bash
pip install hatch
```

Then create the virtual environment:

```bash
hatch env create
```

> This will install `pytest` and other dev dependencies.

---

## Running Tests

There are two test commands:

- **Run tests normally:**

  ```bash
  hatch run test
  ```

- **Generate reference files:**

  ```bash
  hatch run gen
  ```

Tests compare lexer output to expected golden files under `tests/examplefiles`.


## Build and Publish

To build the distribution:

```bash
hatch build
```

To publish to [PyPI.org](https://pypi.org):

```bash
hatch publish
```

---

## Contributing

Feel free to open pull requests for:
- Language updates or extensions
- Additional tests
- Bug fixes

---

