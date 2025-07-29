# # # # # # # # # # # # # # # # # # # #
# Pape Docs
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A module that provides the `TemplateLoader` class and a convenience function."""

import importlib.resources
from datetime import datetime
from importlib.abc import Traversable

import click
import pape.utilities
import tzlocal

TEMPLATES_DIR = importlib.resources.files("pape_docs") / "templates"


def generate_document_content(
    *,
    templates_dir: Traversable = TEMPLATES_DIR,
    doc_type: str | None = None,
) -> str:
    """Invoke a convenience function for `TemplateLoader.generate_document_content`."""
    return TemplateLoader(
        templates_dir=templates_dir,
    ).generate_document_content(with_doc_type=doc_type)


class TemplateLoader:
    """A class for loading and partially filling out the `doc.md` template."""

    def __init__(
        self,
        *,
        templates_dir: Traversable = TEMPLATES_DIR,
    ) -> None:
        """Create a template loader from a directory containing the main template."""
        self.templates_dir = templates_dir

    def generate_document_content(
        self,
        *,
        with_doc_type: str | None = None,
    ) -> str:
        """Read template content and insert dynamic values."""
        doc_type = with_doc_type
        template_file = self.templates_dir / "doc.md"

        if not template_file.is_file():
            click.echo(f"Error: Template file '{template_file}' not found.")
            raise click.Abort

        with template_file.open("r", encoding="utf-8") as f:
            template_content = f.read()

        today_date_str = pape.utilities.ap_style_date_string(
            datetime.now(tzlocal.get_localzone()),
            relative_to=False,
        )
        new_doc_content = template_content.replace("<!-- date -->", today_date_str)

        if doc_type:
            new_doc_content = new_doc_content.replace("<!-- doc type -->", doc_type)
            if doc_type.lower().startswith(("a", "e", "i", "o", "u")):
                new_doc_content = new_doc_content.replace("A(n)", "An")
            else:
                new_doc_content = new_doc_content.replace("A(n)", "A")

        return new_doc_content
