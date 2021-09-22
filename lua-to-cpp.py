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
            property["constructor_value"] = f"{property['default']:.6f}f"
        elif prop_type.lower() == "string":
            property["cpp_type"] = "std::string"
            property["constructor_value"] = f"\"{property['default']}\""
        elif prop_type.lower() == "boolean":
            property["cpp_type"] = "bool"
            property["constructor_value"] = f"{str(property['default']).lower()}"
        else:
            secho(f"Unknown property type in YAML: {prop_type}",
                  fg="red", bold=True)
            sys.exit(1)
    return property_list


# Define our template set.
TEMPLATE_SET = {
    "cpp_class.cpp.j2": {
        "output_file": "%cpp_name.cpp"
    },
    "cpp_class.hpp.j2": {
        "output_file": "%cpp_name.hpp",
    },
    "example.lua.j2": {
        "output_file": "example.lua",
    },
    "example.cpp.j2": {
        "output_file": "example.cpp",
    },
    "build_example.sh.j2": {
        "output_file": "build_example.sh",
    },
}


def load_templates_or_die():
    loaded_templates = {}
    templates_base_dir = "templates"
    for template_file, details in TEMPLATE_SET.items():
        try:
            template_path = os.path.join(templates_base_dir, template_file)
            # Add the loaded Template to the details
            details["template"] = Template(
                open(template_path, 'r').read().strip(),
            )
            loaded_templates[template_file] = details
        except Exception as e:
            secho("\nThere was an issue loading the base templates!",
                  fg="red", bold=True)
            secho(f"{e}\n")
            secho("!!! Aborted !!!")
            sys.exit(1)
    return loaded_templates


def load_class_spec_from_yaml(yaml_file_obj):
    # TODO: Exception handling
    info = yaml.load(yaml_file_obj, Loader=yaml.Loader)
    return info


def determine_file_name(class_spec, supplied_fname):
    file_name = supplied_fname

    if file_name.startswith('%'):
        lookup_property, filename_end = file_name.split('.', 1)
        lookup_property = lookup_property[1:]
        file_name = class_spec[lookup_property]
        file_name = ".".join([file_name, filename_end])
    return file_name


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
    loaded_templates = load_templates_or_die()

    # Load our YAML file and remove one layer of dictionary keys
    class_spec = load_class_spec_from_yaml(in_file)
    class_spec = class_spec["class"]

    # Modify properties list in-place, mapping Lua types to C++ types
    class_spec["properties"] = map_lua_type_to_cpp_type(class_spec["properties"])

    for template_file, template_details in loaded_templates.items():
        template = template_details["template"]
        gen_output = template.render(class_spec=class_spec,
                                     property_list=class_spec["properties"],
                                     lua_table_name=class_spec["lua_table_name"])
        # Write the generated header file to disk
        generated_file = determine_file_name(class_spec, template_details["output_file"])

        gen_out_path = os.path.join(output_dir, f"{generated_file}")
        with open(gen_out_path, "w") as gen_out_file:
            gen_out_file.write(gen_output)
            secho(f"Wrote {len(gen_output)} bytes to {gen_out_path}",
                  fg="green", bold=True)


if __name__ == "__main__":
    main()