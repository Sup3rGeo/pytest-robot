#def pytest_addoption(parser):
#    parser.addoption("--robot-variable", action="store", default=None,
#                     help="Robot variables")

#def pytest_configure(config):
#    config.option.variables


def pytest_collect_file(path, parent):
    if path.ext == ".robot":
        ihook = parent.session.gethookproxy(path)
        return ihook.pytest_pycollect_makemodule(path=path, parent=parent)
