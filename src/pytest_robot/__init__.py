import os
from collections import namedtuple
import robot.parsing.populators as pop
import robot.parsing.model as mod
from importlib.util import find_spec
from pytest_robot.utils import to_snake_case, format_robot_args, get_var_name


# Pytest finding a .robot file with *** Test Cases *** trigger the
# creation of robot2py for this test module, which triggers the
# creation of robot2py for all used resource files

def ensure_resource_as_py(name):
    if find_spec(name):
        # Probably already robot2py-thonized
        return

    abs_resource_path = find_syspath(name)
    robot2py(abs_resource_path)  # Creates pure py module

    if not find_spec(name):
        raise Exception("Problem with Resource file")


def import_all_from_obj(obj, globals):
    methods = {method_name: getattr(obj, method_name)
               for method_name in obj.__dir__()
               if (not method_name.startswith("_")) and callable(getattr(obj, method_name))}
    globals.update(methods)


def robot2py(file_path, session_vars):

    robot_files = []
    output_file_lines = []

    file = mod.TestCaseFile()
    filepop = pop.FromFilePopulator(file)
    filepop.populate(file_path)

    for var, val in session_vars.items():
        output_file_lines.append("{} = {}".format(var, val))

    if file.imports.data:
        output_file_lines.append("\n### IMPORTS ###\n")

    for _import in file.imports.data:
        if _import.type == "Library":
            # Check if is module or class

            try:
                spec = find_spec(_import.name)
            except ModuleNotFoundError:
                spec = None
            if spec:
                output_file_lines.append("from {} import *".format(_import.name))
            else:
                # Try with class
                path_items = _import.name.split(".")
                cls = path_items.pop()
                if not path_items:
                    output_file_lines.append('raise ImportError("Could not import {}")'.format(_import.name))
                    continue

                module = ".".join(path_items)
                try:
                    spec = find_spec(module)
                except ModuleNotFoundError:
                    spec = None
                if not spec:
                    output_file_lines.append('raise ImportError("Could not import {}")'.format(_import.name))
                    continue

                output_file_lines.append("import {}".format(module))
                args = ", ".join(_import.args)
                output_file_lines.append("import_all_from_obj({}({}), globals())".format(_import.name, args))
        elif _import.type == "Resource":
            ensure_resource_as_py(_import.name)
            output_file_lines.append("from {} import *".format(_import.name))

    if file.variable_table.variables:
        output_file_lines.append("\n### VARIABLES ###\n")

    for variable in file.variable_table.variables:
        name = get_var_name(variable.name)
        value = variable.value[0].replace("${", "{").lower()
        output_file_lines.append("{} = f'{}'".format(name, value))

    if file.keywords:
        output_file_lines.append("\n### KEYWORDS ###\n")

    for keyword in file.keywords:
        keyword_func = to_snake_case(keyword.name)
        args = format_robot_args(keyword.args.value)
        output_file_lines.append("def {}({}):".format(keyword_func, args))
        for step in keyword.steps:
            func = to_snake_case(step.name)
            args = format_robot_args(step.args)
            src = "{}({})".format(func, args)
            output_file_lines.append("    {}".format(src))
        output_file_lines.append("\n")

    if file.testcase_table.tests:
        output_file_lines.append("\n### TEST CASES ###\n")

    for test in file.testcase_table.tests:
        test_func = to_snake_case(test.name)
        output_file_lines.append("def {}:".format(test_func))
        for step in test.steps:
            func = to_snake_case(step.name)
            args = format_robot_args(step.args)
            src = "{}({})".format(func, args)
            output_file_lines.append("    {}".format(src))
        output_file_lines.append("\n")

    file_name, _ = os.path.splitext(file_path)
    file_name = "{}.py".format(file_name)
    print(file_name)
    with open(file_name, "w") as f:
        f.write("\n".join(output_file_lines))

    robot_files.append(file)

    return namedtuple("robot2py", "robot_files, path")(robot_files=robot_files, path=file_name)

