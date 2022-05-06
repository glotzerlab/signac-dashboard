# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.

from markupsafe import escape
from werkzeug.utils import cached_property, import_string


def simplified_keys(project):
    sps = list(project.find_statepoints())
    varied_keys = list()
    for key in sps[0]:
        same_for_all = True  # This key has the same value for all statepoints
        for sp in sps:
            if sps[0][key] != sp[key]:
                same_for_all = False
                break
        if not same_for_all:
            varied_keys.append(key)
    return varied_keys


def ellipsis_string(string, length=60):
    string = str(string)
    half = int(length / 2)
    if len(string) < length:
        return string
    else:
        return string[:half] + "..." + string[-half:]


def escape_truncated_values(dic, max_chars):
    if max_chars is not None and int(max_chars) > 0:
        for key in dic:
            if len(str(dic[key])) > max_chars:
                dic[key] = (
                    str(escape(ellipsis_string(dic[key], length=max_chars)))
                    + " <em>[Truncated]</em>"
                )
    else:
        for key in dic:
            dic[key] = escape(dic[key])
    return dic


class LazyView:
    # See https://flask.palletsprojects.com/en/2.1.x/patterns/lazyloading/
    def __init__(self, dashboard, import_name):
        self.__module__, self.__name__ = import_name.rsplit(".", 1)
        self.import_name = import_name
        self.dashboard = dashboard

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        kwargs.update({"dashboard": self.dashboard})
        return self.view(*args, **kwargs)
