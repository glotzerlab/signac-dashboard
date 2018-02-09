# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import unittest
import tempfile
import shutil

from signac_dashboard import Dashboard
from signac import init_project


class DashboardTestCase(unittest.TestCase):

    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        project = init_project('dashboard-test-project',
                               root=self._tmp_dir,
                               make_dir=False)
        config = {}
        modules = []
        self.dashboard = Dashboard(config=config,
                                   project=project,
                                   modules=modules)
        self.test_client = self.dashboard.app.test_client()
        self.addCleanup(shutil.rmtree, self._tmp_dir)

    def tearDown(self):
        pass

    def test_get_jobs(self):
        rv = self.test_client.get('/jobs', follow_redirects=True)
        assert b'dashboard-test-project' in rv.get_data()


if __name__ == '__main__':
    unittest.main()
