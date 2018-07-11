# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import sys

from . import Dashboard
import signac


def main():
    try:
        project = signac.get_project()
    except LookupError:
        print('No signac project could be found in the current directory.')
        sys.exit(1)

    modules = []
    if 'dashboard' not in project.document:
        # Initialize a new Dashboard using essential modules
        from .modules import StatepointList, DocumentList
        modules.append(StatepointList())
        modules.append(DocumentList())
    Dashboard(modules=modules).main()


if __name__ == '__main__':
    main()
