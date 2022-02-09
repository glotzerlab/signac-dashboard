# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import os

from setuptools import find_packages, setup

requirements = [
    "flask>=1.0",
    "flask-assets>=2.0",
    "flask-turbolinks",
    "jsmin",
    "libsass",
    "natsort",
    "signac>=1.0",
    "watchdog",
    "webassets>=2.0",
    "werkzeug>=1.0",
]

description = "Visualize data spaces in a web browser."

try:
    this_path = os.path.dirname(os.path.abspath(__file__))
    fn_readme = os.path.join(this_path, "README.md")
    with open(fn_readme) as fh:
        long_description = fh.read()
except OSError:
    long_description = description


setup(
    name="signac-dashboard",
    version="0.2.9",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7,<4",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    author="Bradley Dice",
    author_email="bdice@bradleydice.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="visualization dashboard signac framework",
    url="https://signac.io",
    entry_points={
        "console_scripts": [
            "signac-dashboard = signac_dashboard.__main__:main",
        ],
    },
)
