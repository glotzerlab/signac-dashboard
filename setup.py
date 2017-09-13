# Copyright (c) 2017 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 4, 0):
    print("Error: signac-dashboard requires Python version >= 3.4")
    sys.exit(1)


setup(
    name='signac-dashboard',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'signac>=0.8',
        'flask',
        'Flask-Assets',
        'Flask-Cache',
        'Flask-Turbolinks',
        'libsass',
        'cssmin',
        'jsmin'
    ],

    author='Bradley Dice',
    author_email='bdice@bradleydice.com',
    description="Data visualization based on signac.",
    keywords='visualization dashboard signac framework',
    url='https://bitbucket.org/bdice/signac-dashboard',

)
