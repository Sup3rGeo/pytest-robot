import os
import ast
import astunparse
import sys
from collections import namedtuple

from importlib import import_module
from importlib.machinery import SourceFileLoader

from rflint.parser import RobotFactory
from pytest_robot.utils import change_case, format_robot_args, get_var_name


generate_py = True

# session variables used by robot2py function.
# should be filled by other modules
session_vars = {}


def import_all_from(lib_str, globals, args=()):
    """ Used by python-converted robot files to import libraries
    as a module or class object """
    __tracebackhide__ = True

    path_items = lib_str.split(".")
    try:
        # try module
        obj = import_module(lib_str)
    except ImportError:
        # try class
        cls_name = path_items.pop()
        package_name = ".".join(path_items)
        try:
            if package_name:
                package = import_module(package_name)
                cls = getattr(package, cls_name)
            else:
                cls = getattr(globals, cls_name)
        except AttributeError:
            raise ImportError("Cannot import class/module '{}'".format(lib_str)) from None
        args = ", ".join(args)
        obj = cls(*args)

    callables = {name: getattr(obj, name)
                for name in obj.__dir__()
                if (not name.startswith("_")) and callable(getattr(obj, name))}
    globals.update(callables)


class RobotAstModule(object):

    def __init__(self, filename):
        self.filename = filename
        self.module = ast.parse("")

    def parse(self, src):
        return ast.parse(src, self.filename)

    def create_function(self, name, args, funclineno, argslineno):
        node = self.parse("def {}({}):\n    pass".format(name, args)).body[0]
        node.body.pop()
        node.lineno = funclineno
        node.col_offset = 1
        # TODO: Search all args and set lineno
        self.module.body.append(node)
        self.current_function = node

    def add_line_to_current_function(self, src, lineno):
        node = self.parse(src).body[0]
        node.lineno = lineno
        node.col_offset = 1
        self.current_function.body.append(node)

    def add_line_to_module(self, src, lineno):
        node = self.parse(src).body[0]
        node.lineno = lineno
        node.col_offset = 1
        self.module.body.append(node)

    def get_code(self):
        return self.module


def robot2py(file_path, session_vars):
    """ Main function that generates python source from
    robot file."""

    print("ROBOT2PY with {}".format(file_path))

    robot_files = []
    output_file = RobotAstModule(filename=file_path)

    file = RobotFactory(file_path)

    output_file.add_line_to_module("from pytest_robot import import_all_from", lineno=1)
    output_file.add_line_to_module("import pytest", lineno=1)
    for var, val in session_vars.items():
        output_file.add_line_to_module("{} = {}".format(var, val), lineno=1)

    for table in file.tables:
        if table.name == "settings":
            for stmt in table.statements:
                stmt_type, *stmt_args = stmt
                if stmt_type == "Documentation":
                    output_file.add_line_to_module('"""{}"""'.format("\n".join(stmt_args)), lineno=stmt.startline)
                elif stmt_type == "Library" or stmt_type == "Resource":
                    lib, *lib_args = stmt_args
                    output_file.add_line_to_module('import_all_from("{}", globals(), {})'.format(lib, lib_args), lineno=stmt.startline)
                else:
                    raise Exception("Statement {} not supported".format(stmt))
        elif table.name == "Keywords":
            for keyword in table.keywords:
                keyword_func = change_case(keyword.name, lower=False, space="", camel2snake=False)
                args = None
                docstring = None
                for stmt in keyword.settings:
                    _, stmt_type, *stmt_args = stmt
                    if stmt_type == "[Arguments]":
                        args = format_robot_args(stmt_args)
                    elif stmt_type == "[Documentation]":
                        docstring = '"""{}"""'.format("\n".join(stmt_args))
                    else:
                        raise Exception("Statement {} not supported. {} {}".format(stmt, stmt_type, stmt_args))
                output_file.create_function(keyword_func, args, funclineno=keyword.linenumber, argslineno=1)
                #if docstring:
                #    output_file.add_line_to_current_function(docstring, lineno=1)
                for stmt in keyword.steps:
                    if len(stmt) == 1 and stmt[0] == "":
                        # Null statement
                        continue
                    _, step_name, *step_args = stmt
                    func = change_case(step_name)
                    args = format_robot_args(step_args)
                    src = "{}({})".format(func, args)
                    output_file.add_line_to_current_function(src, lineno=1)
        elif table.name == "Test Cases":
            for test_case in table.testcases:
                func = change_case(test_case.name, lower=False, space="", camel2snake=False)
                args = ""
                docstring = None
                tags = None
                for stmt in test_case.settings:
                    _, stmt_type, *stmt_args = stmt
                    if stmt_type == "[Arguments]":
                        args = format_robot_args(stmt_args)
                    elif stmt_type == "[Documentation]":
                        docstring = '"""{}"""'.format("\n".join(stmt_args))
                    elif stmt_type == "[Tags]":
                        tags = stmt_args
                    elif stmt_type == "[Timeout]":
                        pass
                    else:
                        raise Exception("Statement {} not supported. {} {}".format(stmt, stmt_type, stmt_args))
                #for tag in tags:
                #    output_file.add_line_to_module("@pytest.mark.{}".format(tag.replace(" ","")), lineno=1)
                #if docstring:
                #    output_file.add_line_to_current_function(docstring, lineno=1)
                # Todo: make decorators and docstring part of the ast function creation
                output_file.create_function("test_{}".format(func), args, funclineno=test_case.linenumber, argslineno=1)
                for stmt in test_case.steps:
                    if len(stmt) == 1 and stmt[0] == "":
                        # Null statement
                        continue
                    _, step_name, *step_args = stmt
                    func = change_case(step_name)
                    args = format_robot_args(step_args)
                    src = "{}({})".format(func, args)
                    output_file.add_line_to_current_function(src, lineno=stmt.startline)


    file_name, _ = os.path.splitext(file_path)
    file_name = "{}.robot.py".format(file_name)

    source = astunparse.unparse(output_file.get_code())
    output_ast = output_file.get_code()

    if generate_py:
        with open(file_name, "w") as f:
            f.write(source)

    robot_files.append(file)

    return namedtuple("robot2py", "source, robot_files, path, ast")(source=source, robot_files=robot_files, path=file_name, ast=output_ast)


class RobotLoader(SourceFileLoader):
    def get_code(self, fullname):
        source_path = self.get_filename(fullname)
        filename = os.path.basename(source_path)
        module_ast = robot2py(source_path, {}).ast
        return compile(module_ast, filename, "exec")



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

