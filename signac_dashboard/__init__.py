# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from .dashboard import Dashboard
from .module import Module
from . import modules


__version__ = '0.1.4'

__all__ = [
    '__version__',
    'Dashboard',
    'Module',
    'modules',
]
