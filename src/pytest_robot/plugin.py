from pytest_robot import robot2py


#def pytest_addoption(parser):
#    parser.addoption("--robot-variable", action="store", default=None,
#                     help="Robot variables")

#def pytest_configure(config):
#    config.option.variables

session_vars = {
    "TARGET": "typhoonhilkeywords",
    "RESOURCES": "resources"
}

def pytest_collect_file(parent, path):
    if path.ext == ".robot":
        file = robot2py(path, session_vars).path
        ihook = parent.session.gethookproxy(path)
        return ihook.pytest_pycollect_makemodule(path=file, parent=parent)
