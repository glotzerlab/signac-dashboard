import os
import pytest

from tempfile import TemporaryDirectory

import signac
from signac._config import _load_config

from signac_dashboard.modules import Navigator



class TestNavigator:
    ignore = None
    sp_list = []
    @pytest.fixture(autouse=True)
    def setUp(self, request):
        self._tmp_dir = TemporaryDirectory(prefix="signac_")
        request.addfinalizer(self._tmp_dir.cleanup)
        self._tmp_pr = os.path.join(self._tmp_dir.name, "pr")
        os.mkdir(self._tmp_pr)
        self.config = _load_config()
        self.project = signac.init_project(path=self._tmp_pr)
        
        self.init_list(self.sp_list)

        # subclass variable
        self.navigator = Navigator(ignore=self.ignore)

    def init_list(self, sp_list):
        for sp in sp_list:
            self.project.open_job(sp).init()

    # def test_shadow_project(self):
    #     pass

    # def test_neighbor_list(self):
    #     pass


class BadCases(TestNavigator):
    def test_shadow_project(self):
        with pytest.raises(ValueError):
            self.navigator.prepare_shadow_project(self.project)

class TestEmptyProject(TestNavigator):
    ignore = "a"
    sp_list = []
    def test_shadow_project(self):
        shadow_map, shadow_cache = self.navigator.prepare_shadow_project(self.project)
        assert shadow_map == {}
        assert shadow_cache == {}

class TestNoIgnore(TestNavigator):
    ignore = None
    sp_list = [{"a": 1, "seed": 0},
               {"a": 2, "seed": 1}]
    def test_neigbor_list(self):
        pass

class TestIgnoreUselessKey(TestNavigator):
    ignore = "not_in_project"
    sp_list = [{"a": 1, "seed": 0},
               {"a": 2, "seed": 1}]


class TestIgnoreSeed(TestNavigator):
    ignore = "seed"
    sp_list = [{"a": 1, "seed": 0}, # 7af33fa439e2c0bb69e9f865563e13bd
               {"a": 2, "seed": 1}] # 53b5effad94d233cead26298d23a2832
    def test_shadow_project(self):
        shadow_map, shadow_cache = self.navigator.prepare_shadow_project(self.project)
        assert shadow_map == {'9f8a8e5ba8c70c774d410a9107e2a32b': '53b5effad94d233cead26298d23a2832',
                                   '42b7b4f2921788ea14dac5566e6f06d0': '7af33fa439e2c0bb69e9f865563e13bd'}
        assert shadow_cache == {'9f8a8e5ba8c70c774d410a9107e2a32b': {'a': 2},
                                     '42b7b4f2921788ea14dac5566e6f06d0': {'a': 1}}

    def test_neighbor_list(self):
        shadow_map, shadow_cache = self.navigator.prepare_shadow_project(self.project)
        sorted_schema = {"a": [1,2], "seed": [0,1]}
        self.navigator.make_neighbor_list(shadow_map, shadow_cache, sorted_schema)


class TestIgnoreParallel(TestNavigator):
    ignore = "2a"
    sp_list = [{"a": 1, "2a": 2},
               {"a": 2, "2a": 4}]
    
class TestIgnoreSeedBad(BadCases):
    ignore = "seed"
    sp_list = [{"a": 1, "seed": 0},
               {"a": 1, "seed": 1}]

class TestIgnoreParallelBad(BadCases):
    ignore = "2a"
    sp_list = [{"a": 1, "2a": 2},
               {"a": 1, "2a": 3}]

    


