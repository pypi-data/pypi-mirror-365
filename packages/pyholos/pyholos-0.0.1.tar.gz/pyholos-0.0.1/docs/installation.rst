.. include:: common.rst

############
Installation
############

*************
Prerequisites
*************


Git |git|
=========

.. |git| image:: figs/logo_git.png
    :class: no-scaled-link
    :height: 2ex

**Git** is a free and open source distributed version control system that allows versioning your code.
Ensure that ``git`` executable is installed: open a terminal (e.g. Windows PowerShell) and type :code:`git --version`.

If **Git** is not installed, you may install it following the instructions
`here <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__.

conda |conda|
=============

.. |conda| image:: figs/logo_conda.png
    :class: no-scaled-link
    :height: 2ex


**conda** is a package and environment manager. It allows to create environments, install |python| packages
and their dependencies within these environments. **miniconda** is a free minimal installer for **conda**.

Ensure that ``conda`` executable is installed by typing in a terminal :code:`conda --version`.
If ``conda`` is not installed (command not found) you can install it by following `these instructions
<https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation>`__ (install
``miniconda``).


Once **miniconda** installed, you will be able to see an *Anaconda Powershell Prompt (Miniconda3)* added to your system.
This terminal will allow you to run ``conda`` commands. You may also execute ``conda`` with other terminals.
In order to do so, type in *Anaconda Powershell Prompt (Miniconda3)* :code:`conda init` (refer to this `doc
<https://docs.conda.io/projects/conda/en/latest/dev-guide/deep-dives/activation.html>`__ for details).


GitHub |github|
===============

.. |github| image:: figs/logo_github.png
    :class: no-scaled-link
    :height: 2ex


You must also ensure that you have a valid **GitHub**. You can create your account by the instructions
`here <https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github>`__.

It is recommended to clone projects from **GitHub** using the Secure Shell Protocol (SSH) protocol. Ensure that
your **GitHub** profile has a public SSH key linked to a private key locally. Check out your existing SSH keys by
going to your **GitHub** profile settings:

.. image:: figs/ssh_keys.png
    :align: center

|

For more details on how to check if you have existing SSH keys, refer to the instructions `here
<https://docs.github.com/en/authentication/connecting-to-github-with-ssh/checking-for-existing-ssh-keys>`__.

If you want to create an new pair of SSH-keys, please follow the instructions `here
<https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent>`__.


PyCharm |pycharm|
=================

.. |pycharm| image:: figs/logo_pycharm.png
    :class: no-scaled-link
    :height: 2ex


**PyCharm** is an integrated development environment (IDE) used for programming in |python|. It provides powerful
facilities for code analysis, debugging, testing and versioning, among others.

To install **PyCharm**, you will have to download the executable from `here
<https://www.jetbrains.com/pycharm/download/>`__ (Professional or Community edition) and then execute it in your PC.


*********
Holos CLI
*********

Before using PyHolos, the user needs to install Holos CLI. This can be performed by hitting
`this link <https://agriculture.canada.ca/holos/cli/setup.exe>`__.

Once the installation terminated, the user needs to identify the location of the Holos CLI executable (H.CLI.exe) and
to add its path to the environment variables with the name **PATH_HOLOS_CLI**:

.. _fig_environment_variables:

.. figure:: figs/environment_variables.png
    :align: center

    The environment variables that should be added so the system.
    The variable **PATH_HOLOS_CLI** is mandatory while **PATH_HOLOS_SERVICE_RESOURCES** is optional and depends on the
    intended usage of PyHolos (see :ref:`installation:Soil data files` below).


*******************
The PyHolos package
*******************

Go the folder where you would like to clone ``PyHolos``. Right-click on the window and open a terminal then
type:

.. code-block:: bash

    git clone git@github.com:ProjetSOM/scenarios_virtual.git


Move inside the project folder:


.. code-block:: bash

    cd pyholos


Now you can create a **conda** (or **mamba**) environment inside which you will install ``pyholos`` and all its
dependencies. Let's create and activate an environment called 'MyEnv':


.. code-block:: bash

    conda create -n MyEnv python pip
    conda activate MyEnv



Now install the dependencies using ``pip``:

.. code-block:: bash

    pip install -r requirements.txt



Finally, install ``pyholos``:

.. code-block:: bash

    pip install -e .


You're done installing the package!

Launch now PyCharm |pycharm| and open the package folder as a project:

.. image:: figs/pycharm_open_project.png
    :align: center

|

Go now to:

**File** |rarr| **Settings** |rarr| **Project: scenario_virtual/Python** |rarr| **interpreter** |rarr| **Add Interpreter** |rarr| **Add local Interpreter...**

then choose **Virtualenv Environment** and pick an **Existing** environment.
Under |windows|, the **conda** environment interpreter that you need must be situated under :

**C:\\Users\\<YourUserName>\\AppData\\Local\\miniconda3\\envs\\<YourEnvironmentName>\\python.exe**

.. image:: figs/pycharm_add_interpreter.png
    :align: center

|

.. |windows| image:: figs/logo_windows.png
    :class: no-scaled-link
    :height: 2ex

.. note::
    **pip** is another package manager (often faster) for installing package dependencies than **conda**. It can be
    installed within a **conda** environment.

.. note::

    In the future, `pyholos` will be deployed to third-party software repositories (e.g. PyPI). Meanwhile, the user will
    need to clone the source code in order to build it locally.


.. code-block:: bash

    cd <directory_where_pyholos_will_be_cloned>
    git clone git@github.com:Mon-Systeme-Fourrager/holos_service.git
    cd holos_service
    pip install -e .


***************
Soil data files
***************

.. |slc| replace:: `SLC <https://open.canada.ca/data/en/dataset/5ad5e20c-f2bb-497d-a2a2-440eec6e10cd>`__

Soil data is required when using PyHolos to create inputs for Holoc CLI. As in the C# source code of Holos, PyHolos uses
the data provided by the Soil Landscapes of Canada (|slc|).
Two types of data are required, respectively CSV and GeoJSON types.
The CSV files include soil information per polygon and can be downloaded by hitting "Pre-packaged CSV files" in |slc|
(downloads a zip file called "soil_landscapes_of_canada_v3r2_csv.zip").
The GeoJSON file includes complimentary spatially-identified soil information, downloadable by hitting
"Pre-packaged GeoJSON files" in |slc|
(downloads a zip file called "soil_landscapes_of_canada_v3r2_geojson.zip").

.. note::
    For convenience the soil data are already added to this project under ``src/pyholos/resources``. Prior to using
    PyHolos, extract the zipped SLC files ``soil_landscapes_of_canada_v3r2_geojson.zip`` and remove the zip file.
    **The soil data files are only required when PyHolos is used to create input files for Holos CLI.**

    .. image:: figs/location_slc_data.png
        :align: center
        :height: 400
