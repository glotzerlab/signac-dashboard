# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.

import flask_login
from markupsafe import escape
from werkzeug.utils import cached_property, import_string


def simplified_keys(project):
    sps = list(project.find_statepoints())
    varied_keys = []
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


def escape_truncated_values(data, max_chars):
    """Truncate values in a dict to a maximum number of characters."""
    if max_chars is not None and int(max_chars) > 0:
        for key in data:
            if len(str(data[key])) > max_chars:
                data[key] = (
                    str(escape(ellipsis_string(data[key], length=max_chars)))
                    + " <em>[Truncated]</em>"
                )
    else:
        for key in data:
            data[key] = escape(data[key])
    return data


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
        # Protect routes added in the format self.add_url("views.home", ["/"])
        if not flask_login.current_user.is_authenticated:
            return self.dashboard.login_manager.unauthorized(), 401

        kwargs.update({"dashboard": self.dashboard})
        return self.view(*args, **kwargs)
