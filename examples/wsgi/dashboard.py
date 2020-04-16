#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList

# To use multiple workers, a single shared key must be used. By default, the
# secret key is randomly generated at runtime by each worker. Using a provided
# shared key allows sessions to be shared across workers. This key was
# generated with os.urandom(16)
config = {
    'SECRET_KEY': b"\x99o\x90'/\rK\xf5\x10\xed\x8bC\xaa\x03\x9d\x99"
}

modules = [
    StatepointList(),
]

# The dashboard instance must be importable by the WSGI server.
dashboard = Dashboard(config=config, modules=modules)
