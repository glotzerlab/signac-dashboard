#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import signac

project = signac.init_project()

for i in range(10):
    job = project.open_job({"step": i})
    job.doc["step"] = i
