# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import os
from setuptools import setup, find_packages

description = 'Data visualization based on signac.'

try:
    this_path = os.path.dirname(os.path.abspath(__file__))
    fn_readme = os.path.join(this_path, 'README.md')
    with open(fn_readme) as fh:
        long_description = fh.read()
except (IOError, OSError):
    long_description = description


setup(
    name='signac-dashboard',
    version='0.2.7',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'signac>=1.0',
        'Flask>=1.0',
        'Flask-Assets>=2.0',
        'webassets>=2.0',
        'Flask-Turbolinks',
        'libsass',
        'jsmin',
        'natsort',
        'watchdog',
        'Werkzeug>=1.0',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    author='Bradley Dice',
    author_email='bdice@bradleydice.com',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='visualization dashboard signac framework',
    url='https://signac.io',

    entry_points={
        'console_scripts': [
            'signac-dashboard = signac_dashboard.__main__:main',
        ],
    },
)
