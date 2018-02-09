# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 4, 0):
    print('Error: signac-dashboard requires Python version >= 3.4')
    sys.exit(1)

setup(
    name='signac-dashboard',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'signac>=0.8',
        'Flask>=0.12',
        'Flask-Assets',
        'Flask-Cache',
        'Flask-Turbolinks',
        'libsass',
        'cssmin',
        'jsmin'
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    author='Bradley Dice',
    author_email='bdice@bradleydice.com',
    description='Data visualization based on signac.',
    keywords='visualization dashboard signac framework',
    url='https://bitbucket.org/glotzer/signac-dashboard',

)
