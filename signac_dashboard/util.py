# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.


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
