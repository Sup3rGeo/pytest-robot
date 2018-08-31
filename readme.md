# Description

RobotFramework is an interesting testing framework which is comprised of:

- Keyword-based language for writing tests
- Test runner
- Report generator
- Specific libraries for the Framework

However, although point number 1 is really unique for RobotFramework, it is reinventing the wheel for the other points,
meaning there are many very good project that provides the same funcionality RobotFramework provides:

- Test runner: pytest, also adding parametrization and fixtures
- Report generator: Allure Framework, beautiful interactive reports with plugins to many CI systems
- Specific libraries: These are python libraries with glues to adding data to report. Can be easily made work
with pytest and Allure

Therefore the goal of this project is to run .robot test files (keyword-based language) with Pytest and Allure Framework,
with the following benefits:
- Effectively creates a Keyword-driven framework for pytest
- Enables running pytest tests and robot keyword-driven tests on the same test run, in the same report.
- Can allow extending the robot syntax to take advantage of pytest parametrization and fixtures
- As a side-product, can convert robot files to equivalent python files in order to fully migrate an entire robot
test suite.

This project so far is just a spike to check the feasibility of the
defined approaches. It then will need help with improving and testing.

# Approach

This project is comprised of the following parts:

- Robot file parser
- Custom python loader for .robot files
- Pytest plugin to run .robot files as python tests.
- Adaptation of RobotFramework libraries

### Robot file parser

Originally this project used `robot.parsing` API, which is complete but does not gather the line number of the
rows and column offsets of the cells. Those are important to get meaningful exception messages.

Currently we are using the robot parser from `robotframework-lint` project, which retains line numbers (but not
column offsets yet). This is already good enough for pointing the line with problems in case of errors.

### Custom loader for robot files

For the integration to be as seamless as possible, a python import Loader is defined to recognize .robot files as
python sources and generates a python equivalent version of the robot file on the fly when loading.

This means robot files can be imported just like python files, following all the import rules (as long as they are
found in sys.path).

Originally the conversion was made only on source-level, in such way that a complete python source was created and then
compiled to get the module executable code. This, however, would not allow to have correct line numbers in case of errors.
For this reason, the `robotframework-lint` parser was used and AST nodes are created for each statement, considering the
correct line number. The AST is then compiled to get python executable code for the modules.

### Pytest plugin for .robot files

This was easily implemented by a `pytest_collect_file` that would return default `pytest_pycollect_makemodule` for the
robot file, as it is effectively a python module.

### Adaptation of RobotFramework libraries

RobotFramework libraries can be adapted to the extent where we implement replacements for robot's BuiltIn module (and
monkey patch in runtime). For instance, we could replace the functions:
- Replace the function log() and write() with proper robot framework replacements.
- run_keyword
- get_variable_value

# Some results so far:

{print screens]