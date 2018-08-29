import sys
import os
import pytest_robot

file_path = os.path.abspath(__file__)

for key, value in sys.path_importer_cache.items():
    if "importing_robot" in key.lower():
        print(key)
        print(value)
        print(value._loaders)
        pytest_robot.add_loader(value)

pytest_robot.generate_py = True

import Sample

dir(Sample)
Sample.test_sample_test_1()

