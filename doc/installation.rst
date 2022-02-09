.. _dashboard-installation:

============
Installation
============

The recommended installation method for **signac-dashboard** is via conda_ or pip_.
The software is tested for Python versions 3.7+. Its primary dependencies are signac_ and flask_.
Supported Python and NumPy versions are determined according to the `NEP 29 deprecation policy <https://numpy.org/neps/nep-0029-deprecation_policy.html>`_.

.. _conda: https://docs.conda.io/
.. _conda-forge: https://conda-forge.org/
.. _pip: https://pip.pypa.io/
.. _signac: https://signac.io/
.. _flask: https://flask.palletsprojects.com/

Install with conda
==================

You can install **signac-dashboard** via conda (available on the conda-forge_ channel), with:

.. code:: bash

    $ conda install -c conda-forge signac-dashboard

All additional dependencies will be installed automatically.
To upgrade the package, execute:

.. code:: bash

    $ conda update signac-dashboard


Install with pip
================

To install the package with the package manager pip_, execute

.. code:: bash

    $ pip install signac-dashboard --user

.. note::
    It is highly recommended to install the package into the user space and not as superuser!

To upgrade the package, simply execute the same command with the ``--upgrade`` option.

.. code:: bash

    $ pip install signac-dashboard --user --upgrade


Source Code Installation
========================

Alternatively you can clone the `git repository <https://github.com/glotzerlab/signac-dashboard>`_ and execute the ``setup.py`` script to install the package.

.. code:: bash

  git clone https://github.com/glotzerlab/signac-dashboard.git
  cd signac-dashboard
  git submodule update --init  # This step is required!
  python setup.py install --user
