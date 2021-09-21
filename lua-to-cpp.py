#!/usr/bin/env python3
import sys
import yaml

from jinja2 import Template
import click
from click import secho


def load_templates_or_die():
    try:
        _cpp_template = Template(
            open('templates/cpp_class.cpp.j2', 'r').read().strip(),
        )
        _hpp_template = Template(
            open('templates/cpp_class.cpp.j2', 'r').read().strip(),
        )
        _eg_lua_template = Template(
            open('templates/example.lua.j2', 'r').read().strip(),
        )
    except Exception as e:
        secho("\nThere was an issue loading the base templates!",
              fg="red", bold=True)
        secho(f"{e}\n")
        secho("!!! Aborted !!!")
        sys.exit(1)

@click.command()
@click.argument("in_file", type=click.File("r"), metavar="IN_YAML")
def main(in_file):
    """\b
    \033[1;34m╭────────────╮
    │\033[33m lua-to-cpp \033[34m│▌
    ╰────────────╯▌
     ▀▀▀▀▀▀▀▀▀▀▀▀▀▘\033[0m

    \b
    Creates C++ class and loader function to load a Lua table into a C++
    class, configured using a YAML file to drive everything.
    """
    print(f"Reading class specification from file: {in_file.name}")

    _cpp_template, _hpp_template, _eg_lua_template = load_templates_or_die()


if __name__ == "__main__":
    main()