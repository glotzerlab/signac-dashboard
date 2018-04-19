# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import unittest
import json

from signac_dashboard import Dashboard
import signac_dashboard.modules
from signac_dashboard.module import ModuleEncoder


class ModuleTestCase(unittest.TestCase):

    def test_modules(self):
        modules = []
        for m in signac_dashboard.modules.__all__:
            modules.append(getattr(signac_dashboard.modules, m).__call__())
        json_modules_before = json.dumps(modules, cls=ModuleEncoder,
                                         sort_keys=True, indent=4)
        parsed_modules = Dashboard.decode_modules(json_modules_before)
        json_modules_after = json.dumps(parsed_modules, cls=ModuleEncoder,
                                        sort_keys=True, indent=4)
        assert json_modules_before == json_modules_after


if __name__ == '__main__':
    unittest.main()
