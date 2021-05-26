#!/usr/bin/env python3
# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import signac

project = signac.init_project("awesome-project")

for adverb in ("very", "super", "really", "extremely"):
    job = project.open_job({"awesome_factor": adverb})
    job.init()
