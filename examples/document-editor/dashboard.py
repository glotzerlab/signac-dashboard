#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard import Dashboard
from signac_dashboard.modules import DocumentEditor, DocumentList, StatepointList

if __name__ == "__main__":
    modules = [
        StatepointList(),
        DocumentEditor(),
        DocumentList(),
    ]
    Dashboard(modules=modules).main()
