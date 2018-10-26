.. _installation:

============
Installation
============

The recommended installation method for **signac-dashboard** is via conda_ or pip_.
The software is tested for Python versions 2.7.x and 3.4+.

.. _conda: https://anaconda.org/
.. _pip: https://pip.pypa.io/en/stable/

Install with conda
==================

To install **signac-dashboard** via conda, you first need to add the conda-forge_ channel with:

.. _conda-forge: https://conda-forge.github.io

.. code:: bash

    $ conda config --add channels conda-forge

Once the **conda-forge** channel has been enabled, **signac-dashboard** can be installed with:

.. code:: bash

    $ conda install signac-dashboard

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

Alternatively you can clone the `git repository <https://bitbucket.org/glotzer/signac-dashboard>`_ and execute the ``setup.py`` script to install the package.

.. code:: bash

  git clone https://bitbucket.org/glotzer/signac-dashboard.git
  cd signac-dashboard
  python setup.py install --user
