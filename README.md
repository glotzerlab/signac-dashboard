# README

## About

Data visualization, analysis, and "dashboard" monitoring tool based on the signac and signac-flow frameworks.

The signac-dashboard interface allows users to rapidly view text, image, and potentially interactive content contained in a [signac project](https://glotzerlab.engin.umich.edu/signac).
Additionally, users may monitor the current progress of their work if the signac project is also managed using [signac-flow](https://signac-flow.readthedocs.io/en/latest/).

The software is currently in "alpha."

## Maintainers

  * Bradley Dice (bdice@umich.edu)

## Installation

This software is currently standalone, but may someday be an installable package similar to signac-flow, where users' code includes a class that inherits from the base class implemented in this repository.

Required software for building (may change):
* NodeJS
* [yarn package manager](https://yarnpkg.com/en/).

Build process:
* Run `gulp` and it will compile/combine and copy all CSS/SCSS files, JavaScript files, and image assets to the `static` folder.

Required Python packages for running the server (may change):
* flask
* signac

Run process:
* Run `./webserver.py` and it will launch a server listening on local port 8888.

## Documentation

No formal documentation exists yet.