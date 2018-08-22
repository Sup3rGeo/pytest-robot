from pytest_robot import robot2py
import py
import os

#def pytest_addoption(parser):
#    parser.addoption("--robot-variable", action="store", default=None,
#                     help="Robot variables")

#def pytest_configure(config):
#    config.option.variables

session_vars = {
}

def pytest_collect_file(parent, path):
    if path.ext == ".robot":
        file = robot2py(str(path), session_vars).path
        file = py.path.local(file)
        ihook = parent.session.gethookproxy(path)
        return ihook.pytest_pycollect_makemodule(path=file, parent=parent)
