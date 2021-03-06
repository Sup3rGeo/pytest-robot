import os
import sys
from collections import namedtuple

from importlib import import_module
from importlib.machinery import SourceFileLoader

from robot.api import TestData
from pytest_robot.utils import change_case, format_robot_args, get_var_name


generate_py = True

# session variables used by robot2py function.
# should be filled by other modules
session_vars = {}


def import_all_from(lib_str, globals, args=()):
    """ Used by python-converted robot files to import libraries
    as a module or class object """

    path_items = lib_str.split(".")
    try:
        # try module
        obj = import_module(lib_str)
    except ImportError:
        # try class
        cls_name = path_items.pop()
        package_name = ".".join(path_items)
        if package_name:
            package = import_module(package_name)
            cls = getattr(package, cls_name)
        else:
            cls = getattr(globals, cls_name)
        args = ", ".join(args)
        obj = cls(*args)

    callables = {name: getattr(obj, name)
                for name in obj.__dir__()
                if (not name.startswith("_")) and callable(getattr(obj, name))}
    globals.update(callables)


def robot2py(file_path, session_vars):
    """ Main function that generates python source from
    robot file."""

    print("ROBOT2PY with {}".format(file_path))

    robot_files = []
    output_file_lines = []

    file = TestData(source=file_path)

    output_file_lines.append("from pytest_robot import import_all_from")
    for var, val in session_vars.items():
        output_file_lines.append("{} = {}".format(var, val))

    if file.imports.data:
        output_file_lines.append("\n### IMPORTS ###\n")

    for _import in file.imports.data:
        output_file_lines.append('import_all_from("{}", globals(), {})'.format(_import.name, _import.args))

    if file.variable_table.variables:
        output_file_lines.append("\n### VARIABLES ###\n")

    for variable in file.variable_table.variables:
        name = get_var_name(variable.name)
        value = variable.value[0].replace("${", "{").lower()
        output_file_lines.append("{} = f'{}'".format(name, value))

    if file.keywords:
        output_file_lines.append("\n### KEYWORDS ###\n")

    for keyword in file.keywords:
        keyword_func = change_case(keyword.name)
        args = format_robot_args(keyword.args.value)
        output_file_lines.append("def {}({}):".format(keyword_func, args))
        for step in keyword.steps:
            func = change_case(step.name)
            args = format_robot_args(step.args)
            src = "{}({})".format(func, args)
            output_file_lines.append("    {}".format(src))
        output_file_lines.append("\n")

    if file.testcase_table.tests:
        output_file_lines.append("\n### TEST CASES ###\n")

    for test in file.testcase_table.tests:
        test_func = change_case(test.name, lower=False, space="", camel2snake=False)
        output_file_lines.append("def test_{}():".format(test_func))
        for step in test.steps:
            func = change_case(step.name)
            args = format_robot_args(step.args)
            src = "{}({})".format(func, args)
            output_file_lines.append("    {}".format(src))
        output_file_lines.append("\n")

    file_name, _ = os.path.splitext(file_path)
    file_name = "{}.robot.py".format(file_name)

    source = "\n".join(output_file_lines)

    if generate_py:
        with open(file_name, "w") as f:
            f.write(source)

    robot_files.append(file)

    return namedtuple("robot2py", "source, robot_files, path")(source=source, robot_files=robot_files, path=file_name)


class RobotLoader(SourceFileLoader):
    def get_data(self, path):
        if "pyc" in path:
            return SourceFileLoader.get_data(self, path)
        source = robot2py(path, {}).source
        return source


def add_loader(finder):
    finder._loaders.append(['.robot', RobotLoader])


def upgrade_path_hook(orig_hook):
    def path_hook_for_filehandler_with_robot(path):
        filefinderobj = orig_hook(path)
        add_loader(filefinderobj)
        return filefinderobj

    return path_hook_for_filehandler_with_robot


# Replace original hook with upgraded one
sys.path_hooks[-1] = upgrade_path_hook(sys.path_hooks[-1])


# Remove all cached File finder entries
keys = list(sys.path_importer_cache.keys())
for key in keys:
    sys.path_importer_cache.pop(key)

