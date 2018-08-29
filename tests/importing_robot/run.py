import pytest_robot


pytest_robot.generate_py = True

import Sample

dir(Sample)
Sample.test_sample_test_1()

