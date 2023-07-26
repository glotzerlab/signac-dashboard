# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import json
import re
import shutil
import tempfile
import unittest
from urllib.parse import quote as urlquote

from signac import init_project

import signac_dashboard.modules
from signac_dashboard import Dashboard


class DashboardTestCase(unittest.TestCase):
    def get_response(self, query):
        rv = self.test_client.get(query, follow_redirects=True)
        return str(rv.get_data())

    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self.project = init_project(self._tmp_dir)
        # Set up some fake jobs
        for a in range(3):
            for b in range(2):
                job = self.project.open_job({"a": a, "b": b})
                with job:
                    job.document["sum"] = a + b
        self.config = {"ACCESS_TOKEN": "test"}
        self.modules = []
        self.dashboard = Dashboard(
            config=self.config, project=self.project, modules=self.modules
        )
        self.test_client = self.dashboard.app.test_client()
        self.addCleanup(shutil.rmtree, self._tmp_dir)

        # Test logged out content
        response = self.get_response("/")
        assert "Login required" in response

        response = self.get_response("/jobs/7f9fb369851609ce9cb91404549393f3")
        assert "Login required" in response

        response = self.get_response("/login?token=error")
        assert "Login required" in response
        assert "Incorrect token" in response

        # login
        self.test_client.get("/login?token=test", follow_redirects=True)

    def test_get_project(self):
        rv = self.test_client.get("/project/", follow_redirects=True)
        response = str(rv.get_data())
        assert "signac-dashboard" in response

    def test_get_jobs(self):
        rv = self.test_client.get("/jobs/", follow_redirects=True)
        response = str(rv.get_data())
        assert "signac-dashboard: Jobs" in response

    def test_job_count(self):
        rv = self.test_client.get("/jobs/", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{len(self.project)} jobs" in response

    def test_sp_search(self):
        dictquery = {"a": 0}
        true_num_jobs = len(list(self.project.find_jobs(dictquery)))
        query = urlquote(json.dumps(dictquery))
        rv = self.test_client.get(f"/search?q={query}", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{true_num_jobs} jobs" in response

    def test_doc_search(self):
        dictquery = {"doc.sum": 1}
        true_num_jobs = len(list(self.project.find_jobs(dictquery)))
        query = urlquote(json.dumps(dictquery))
        rv = self.test_client.get(f"/search?q={query}", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{true_num_jobs} jobs" in response

    def test_allow_where_search(self):
        dictquery = {"doc.sum": 1}
        true_num_jobs = len(list(self.project.find_jobs(dictquery)))
        query = urlquote('doc.sum.$where "lambda x: x == 1"')

        self.dashboard.config["ALLOW_WHERE"] = False
        rv = self.test_client.get(f"/search?q={query}", follow_redirects=True)
        response = str(rv.get_data())
        assert "ALLOW_WHERE must be enabled for this query." in response

        self.dashboard.config["ALLOW_WHERE"] = True
        rv = self.test_client.get(f"/search?q={query}", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{true_num_jobs} jobs" in response

    def test_update_cache(self):
        rv = self.test_client.get("/jobs", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{len(self.project)} jobs" in response

        # Create a new job. Because the project has been cached, the response
        # will be wrong until the cache is cleared.
        self.project.open_job({"a": "test-cache"}).init()
        rv = self.test_client.get("/jobs", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{len(self.project)} jobs" not in response

        # Clear cache and try again.
        self.dashboard.update_cache()
        rv = self.test_client.get("/jobs", follow_redirects=True)
        response = str(rv.get_data())
        assert f"{len(self.project)} jobs" in response

    def test_no_view_single_job(self):
        """Make sure View panel is not shown when on a single job page."""
        response = self.get_response("/jobs/7f9fb369851609ce9cb91404549393f3")
        assert "Views" not in response

    def test_logout(self):
        response = self.get_response("/logout")
        if self.dashboard.config.get("ACCESS_TOKEN") is not None:
            assert "Login required" in response


class NoModulesTestCase(DashboardTestCase):
    """Test the inherited tests and cases without any modules."""

    def test_job_sidebar(self):
        response = self.get_response("/jobs/?view=grid")
        assert "No modules." in response

    def test_project_sidebar(self):
        response = self.get_response("/project/")
        assert "No modules." in response
        assert "Views" not in response


class AllModulesTestCase(DashboardTestCase):
    """Add all modules and contexts and test again."""

    def setUp(self):
        self._tmp_dir = tempfile.mkdtemp()
        self.project = init_project(self._tmp_dir)
        # Set up some fake jobs
        for a in range(3):
            for b in range(2):
                job = self.project.open_job({"a": a, "b": b})
                with job:
                    job.document["sum"] = a + b
        self.config = {"ACCESS_TOKEN": None}
        modules = []
        for m in signac_dashboard.modules.__all__:
            module = getattr(signac_dashboard.modules, m)
            for c in module._supported_contexts:
                modules.append(module(context=c))
                with self.assertRaises(RuntimeError):
                    module(context="BadContext")
        self.modules = modules
        self.dashboard = Dashboard(
            config=self.config, project=self.project, modules=self.modules
        )
        self.test_client = self.dashboard.app.test_client()
        self.addCleanup(shutil.rmtree, self._tmp_dir)

    def test_login_with_None_token(self):
        rv = self.test_client.get("/login", follow_redirects=True)
        response = str(rv.get_data())
        assert "signac-dashboard" in response

    def test_module_visible_mobile(self):
        response = self.get_response("/jobs/?view=grid")
        # Check for two instances of Modules header
        pattern = re.compile("Modules</h")
        module_headers = re.findall(pattern, response)
        assert len(module_headers) == 2

    def test_module_selector(self):
        project_response = self.get_response("/project/")
        job_response = self.get_response("/jobs/?view=grid")
        for m in self.modules:
            print(f"Checking for {m.name} in {m.context}.")
            if m.context == "ProjectContext":
                assert m.name in project_response
            elif m.context == "JobContext":
                assert m.name in job_response

    def test_enabled_module_indices_project_session(self):
        """Ensure that the message is not displayed when modules are actually enabled."""
        project_response = self.get_response("/project/")
        assert "No modules for the ProjectContext are enabled." not in project_response

    def test_enabled_module_indices_job_session(self):
        """Ensure that the message is not displayed when modules are actually enabled."""
        job_response = self.get_response("/jobs/?view=grid")
        assert "No modules for the JobContext are enabled." not in job_response

    def test_navigator_module(self):
        """Look for the next and previous values in a table on the page."""
        response = self.get_response("/jobs/017d53deb17a290d8b0d2ae02fa8bd9d")
        assert '<a href="/jobs/fb4e5868559e719f0c5826de08023281"' in response # next job for a = 2
        assert '<a href="/jobs/386b19932c82f3f9749dd6611e846293"' in response # next job for b = 1
        assert 'disabled>min</div>' in response # no previous job for b

if __name__ == "__main__":
    unittest.main()
