#!/usr/bin/env python3
import pprint
import os
import sys
import yaml

from jinja2 import Template
import click
from click import secho


def map_lua_type_to_cpp_type(property_list):
    for property in property_list:
        prop_type = property["type"]
        if prop_type.lower() == "number":
            property["cpp_type"] = "float"
        elif prop_type.lower() == "string":
            property["cpp_type"] = "std::string"
        elif prop_type.lower() == "boolean":
            property["cpp_type"] = "bool"
        else:
            secho(f"Unknown property type in YAML: {prop_type}",
                  fg="red", bold=True)
            sys.exit(1)
    return property_list


def load_templates_or_die():
    try:
        _cpp_template = Template(
            open('templates/cpp_class.cpp.j2', 'r').read().strip(),
        )
        _hpp_template = Template(
            open('templates/cpp_class.hpp.j2', 'r').read().strip(),
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
    return _cpp_template, _hpp_template, _eg_lua_template


def load_class_spec_from_yaml(yaml_file_obj):
    # TODO: Exception handling
    info = yaml.load(yaml_file_obj, Loader=yaml.Loader)
    return info


@click.command()
@click.argument("in_file", type=click.File("r"), metavar="IN_YAML")
@click.option("--output-dir", "-d", "output_dir",
              type=click.Path(file_okay=False, writable=True,
                              resolve_path=True, allow_dash=False),
              default="output", show_default=True,
              help="Specify base directory to write output files to.")
@click.option("--create-output-dir", "-C", "create_out_dir_flag",
              type=bool, is_flag=True,
              default=False, show_default=False,
              help=("Creates target output directory if it doesn't exist."))
def main(in_file, output_dir, create_out_dir_flag):
    """\b
    \033[1;34m╭────────────╮
    │\033[33m lua-to-cpp \033[34m│▌
    ╰────────────╯▌
     ▀▀▀▀▀▀▀▀▀▀▀▀▀▘\033[0m

    \b
    Creates C++ class and loader function to load a Lua table into a C++
    class, configured using a YAML file to drive everything.
    """
    # Basic sanity checks first. Click has checked all our command line args.
    outdir_exists = os.path.exists(output_dir)
    if outdir_exists is False:
        if create_out_dir_flag is False:
            secho(f"The destination output directory, {output_dir}, doesn't"
                  f" exist, and the '--create-output-dir' flag was not "
                  f"provided!")
            sys.exit(1)
        # create the output directory
        os.mkdir(output_dir, 0o755)

    print(f"Reading class specification from file: {in_file.name}")

    # Load the base templates. Any problems are fatal.
    _cpp_template, _hpp_template, _eg_lua_template = load_templates_or_die()

    # Remove one layer of dictionary keys
    class_spec = load_class_spec_from_yaml(in_file)
    class_spec = class_spec["class"]

    # Modify properties list in-place, mapping Lua types to C++ types
    class_spec["properties"] = map_lua_type_to_cpp_type(class_spec["properties"])

    # Render the Header file .hpp template
    hpp_output = _hpp_template.render(
        class_spec=class_spec,
        property_list=class_spec["properties"]
    )

    # Write the generated header file to disk
    hpp_out_path = os.path.join(output_dir, f"{class_spec['cpp_name']}.hpp")
    with open(hpp_out_path, "w") as hpp_file:
        hpp_file.write(hpp_output)
        secho(f"Wrote {len(hpp_output)} bytes to {hpp_out_path}",
              fg="green", bold=True)


if __name__ == "__main__":
    main()