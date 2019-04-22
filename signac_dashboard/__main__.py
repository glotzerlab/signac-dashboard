# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import sys

from . import Dashboard
from .modules import StatepointList, DocumentList, ImageViewer
import signac


def main():
    try:
        project = signac.get_project()
    except LookupError:
        print('No signac project could be found in the current directory.')
        sys.exit(1)

    modules = []
    # Initialize a new Dashboard using essential modules
    modules.append(StatepointList())
    modules.append(DocumentList())
    modules.append(ImageViewer())
    Dashboard(modules=modules, project=project).main()


if __name__ == '__main__':
    main()
