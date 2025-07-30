#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py

A simple command-line tool to render Jinja2 templates.

This script allows for rendering Jinja2 templates from a file or standard input.
It can expose environment variables to the template under the 'env' namespace
when the --env flag is specified.

Usage:
  1. Create a template file, e.g., 'template.j2':
     Hello, my name is {{ env.USER }}.
     I am running this on machine {{ env.HOSTNAME }}.

  2. Run the script with the template:
     export HOSTNAME=$(hostname)
     uvx --from jinja-max j2 --env -i template.j2

     echo "The current path is {{ env.PATH }}" | uvx --from jinja-max j2 --env

Note: Environment variable names in the template are case-sensitive.
      Use the exact case as shown in your environment (e.g., 'USER', 'HOME').
"""

import os
import sys
from pathlib import Path
from typing import Optional

import jinja2
import typer

# Initialize the Typer application
app = typer.Typer(
    name="j2",
    help="A simple CLI tool to render Jinja2 templates.",
    add_completion=False,
)

@app.command()
def main(
    input_file: Optional[Path] = typer.Option(
        None,
        "-i",
        "--input",
        help="Input template file. If not provided, reads from stdin.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    use_env: bool = typer.Option(
        False,
        "--env",
        help="Expose environment variables to the template under the 'env' namespace.",
    ),
):
    """
    Renders a Jinja2 template using environment variables.
    """
    try:
        # --- 1. Read Template Content ---
        if input_file:
            template_content = input_file.read_text()
        else:
            # If no file is provided, check for piped content from stdin
            if sys.stdin.isatty():
                typer.echo(
                    "Error: No input file provided and no data piped to stdin.",
                    err=True
                )
                raise typer.Exit(code=1)
            template_content = sys.stdin.read()

        # --- 2. Prepare Jinja2 Environment and Context ---
        jinja_env = jinja2.Environment()
        template = jinja_env.from_string(template_content)

        context = {}
        if use_env:
            # Expose environment variables under the 'env' key
            context['env'] = dict(os.environ)

        # --- 3. Render and Print Output ---
        rendered_output = template.render(context)
        # Use nl=False to avoid adding an extra newline to the output
        typer.echo(rendered_output, nl=False)

    except jinja2.exceptions.TemplateError as e:
        typer.echo(f"Jinja2 Template Error: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}", err=True)
        raise typer.Exit(code=1)



def main():
    app()

if __name__ == "__main__":
    main()
