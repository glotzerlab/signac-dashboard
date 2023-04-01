# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import sys

import signac

from . import Dashboard
from .modules import DocumentList, ImageViewer, StatepointList


def main():
    try:
        project = signac.get_project()
    except LookupError:
        print("No signac project could be found in the current directory.")
        sys.exit(1)

    # Initialize a new Dashboard using essential modules
    modules = [StatepointList(), DocumentList(), ImageViewer()]
    Dashboard(modules=modules, project=project).main()


if __name__ == "__main__":
    main()
