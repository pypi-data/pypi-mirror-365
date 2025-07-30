
Overview
--------

The **DataFrameViewer** application is a Qt Python application to view, edit, plot,
and filter data from various file types.

The DataFrameViewer utilizes the ``pandas`` module along with the
``Qt for Python`` module to provide a familiar spreadsheet-like GUI for
any type of data that can be stored in a pandas ``DataFrame``.

The intention of this application is to provide a high-performance,
cross-platform application to review and analyze data. The DataFrameViewer
provides a faster and more optimized alternative for viewing and
plotting data files in a table format as opposed to other applications
such as Microsoft Excel or OpenOffice.

Supported Input Formats
~~~~~~~~~~~~~~~~~~~~~~~
::

   Note: Input formats are automatically recognized based on the
   filename.

The Data Viewer currently supports the following input formats:

-  CSV (comma-delimited, tab-delimited)
-  TXT (plain-text files)
-  JSON (Javascript Object Notation)
-  PICKLE (Python Pickle Format)
-  XLSX (Microsoft Excel or OpenOffice files)
-  HDF5 (Hierachical Data Format)

Supported Operating Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following operating systems have been tested and confirmed to
operate the application nominally:

-  Windows 10
-  MacOS Version 11.2 (Big Sur) using Apple M1
-  Linux (CentOS, Ubuntu)

Other operating systems are untested but will likely function if they
are supported by the Qt for Python version documented in
requirements.txt

Setup Instructions
------------------

Dependencies
~~~~~~~~~~~~

-  ``pandas``
-  ``numpy``
-  ``PyQt5``
-  ``openpyxl``
-  ``matplotlib``
-  ``QDarkStyle``

Application Setup / Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: If you are using an Anaconda installation, you can skip these
setup steps and proceed directly to the `Starting the Application`_ section.

The recommended setup method is to use an isolated installation via the `virtualenv`_ module.

.. _virtualenv: https://virtualenv.pypa.io/en/latest/

``virtualenv`` installation on Windows:

.. code:: bash

   virtualenv venv
   source venv/Scripts/activate
   pip install dataframeviewer

``virtualenv`` installation on MacOS / Linux:

.. code:: bash

   virtualenv venv
   source venv/bin/activate
   pip install dataframeviewer

Local installation (on any platform):

.. code:: bash

   pip install dataframeviewer

Installation using a proxy in windows Powershell:

.. code:: bash

   $PROXY="<your-proxy-url>"
   $env:HTTP_PROXY="$PROXY"
   $env:HTTPS_PROXY="$PROXY"
   pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
   pip install dataframeviewer

Starting the Application
------------------------

Run as a module

.. code:: bash

   python -m dataframeviewer

Run with sample data

.. code:: bash

   python -m dataframeviewer --example

Run with input file(s)

.. code:: bash

   python -m dataframeviewer -f file1.csv file2.csv ...

To show the full command line option list

.. code:: bash

   python -m dataframeviewer --help

See the `User Manual`_ for application usage instructions.

.. _User Manual: https://rafyarvelo.gitlab.io/py_data_viewer/user_manual.html#
