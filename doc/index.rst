.. raw:: html

  <h1><img src="_static/logo_horizontal.png" width="30%"></h1>


**Geographic visualizations for HoloViews**


.. notebook:: geoviews ../examples/Homepage.ipynb


Please see the `User Guide <user_guide>`_ for further documentation.

If you have any `issues <https://github.com/holoviz/geoviews/issues>`_ or wish
to `contribute code <https://help.github.com/articles/about-pull-requests>`_., you can visit
our `GitHub site <https://github.com/holoviz/geoviews>`_ or file a topic on
the `HoloViz Discourse <https://discourse.holoviz.org/>`_.

Installation
============

You can install GeoViews and its dependencies using just pip::

    pip install geoviews

Alternatively you can use conda to install geoviews:

    conda install -c pyviz geoviews

Or, the geoviews-core package, which only installs the minimal
dependencies required to run geoviews::

    conda install -c pyviz geoviews-core

Once installed you can copy the examples into the current directory
using the ``geoviews`` command and run them using the Jupyter
notebook::

    geoviews examples
    cd geoviews-examples
    jupyter notebook

(Here `geoviews examples` is a shorthand for `geoviews copy-examples
--path geoviews-examples && geoviews fetch-data --path
geoviews-examples`.)

In the classic Jupyter notebook environment and JupyterLab, first make
sure to load the ``gv.extension()``. For versions of
``jupyterlab>=3.0`` the necessary extension is automatically bundled
in the ``pyviz_comms`` package, which must be >=2.0. However note that
for version of ``jupyterlab<3.0`` you must also manually install the
JupyterLab extension with::

  conda install -c conda-forge jupyterlab
  jupyter labextension install @pyviz/jupyterlab_pyviz

Once you have installed JupyterLab and the extension launch it with::

  jupyter-lab

If you want to try out the latest features between releases, you can
get the latest dev release by specifying `-c pyviz/label/dev` in place
of `-c pyviz`.

Additional dependencies
=======================

If you need to install libraries only available from conda-forge, such
as Iris (to use data stored in Iris cubes) or xesmf, you should
install from conda-forge::

    conda create -n env-name -c pyviz -c conda-forge geoviews iris xesmf
    conda activate env-name

**Note -- Do not mix conda-forge and defaults.** I.e., do not install
packages from conda-forge into a GeoViews environment created with
defaults. If you are using the base environment of mini/anaconda, or
an environment created without specifying conda-forge before defaults,
and you then install from conda-forge, you will very likely have
incompatibilities in underlying, low-level dependencies. These binary
(ABI) incompatibilities can lead to segfaults because of differences
in how non-Python packages are built between conda-forge and defaults.

-----

GeoViews itself is installable using ``pip``, as long as you're using
cartopy>=0.22.0; otherwise you will first need to have installed the
`dependencies of cartopy <http://scitools.org.uk/cartopy/docs/latest/installing.html#requirements>`_,
or have set up your system to be able to build them.

.. toctree::
   :hidden:
   :maxdepth: 2

   Home <self>
   User Guide <user_guide/index>
   Gallery <gallery/index>
   Topics <topics>
   Releases <releases>
   About <about>
