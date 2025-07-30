"""
Config file for testing
"""
from base_config import class_config_2 as class_config_2_

from konfigurator import FieldReference

_work_dir = FieldReference("tests/work_dir")
experiment_dir = _work_dir + "/experiment"

class_config_1 = dict(
    type="tests.test_utils.MyTestClass",
    name="test_instance_1",
)
class_config_2 = class_config_2_
