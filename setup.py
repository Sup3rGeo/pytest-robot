from setuptools import setup, find_packages
import datetime

now = datetime.datetime.now()

NAME = "pytest-robot"
AUTHOR = "Victor Maryama"
COPYRIGHT = "{}, {}".format(now.year, AUTHOR)
DESCRIPTION = "Translates RobotFramework files to plain python."
VERSION = "0.1.0"

setup(
    name=NAME,
    description=DESCRIPTION,
    version=VERSION,
    author=AUTHOR,

    packages=find_packages('src'),
    package_dir={'': 'src'},


    entry_points={
            'pytest11': ['pytest-robot = pytest_robot.plugin']
        },
)
