#!/bin/sh
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
gunicorn --workers 8 --bind localhost:8888 dashboard:dashboard
