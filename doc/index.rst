********
GeoViews
********


**Geographic visualizations for HoloViews**


.. notebook:: geoviews ../examples/Homepage.ipynb


Please see the `User Guide <user_guide>`_ for further documentation.


Installation
------------

You can install GeoViews and its dependencies using conda::

    conda install -c pyviz geoviews

Once installed you can copy the examples into the current directory
using the ``geoviews`` command and run them using the Jupyter
notebook::

    geoviews examples
    cd geoviews-examples
    jupyter notebook

(Here `geoviews examples` is a shorthand for `geoviews copy-examples
--path geoviews-examples && geoviews fetch-data --path
geoviews-examples`.)

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

GeoViews itself is also installable using `pip`, but to do that you
will first need to have installed the [dependencies of cartopy](http://scitools.org.uk/cartopy/docs/v0.15/installing.html#requirements),
or else have set up your system to be able to build them.


Please feel free to report `issues
<https://github.com/ioam/geoviews/issues>`_ or `contribute code
<https://help.github.com/articles/about-pull-requests>`_. You are also
welcome to chat with the developers on `gitter
<https://gitter.im/ioam/holoviews>`_.

.. toctree::
   :hidden:
   :maxdepth: 2

   Introduction <self>
   User Guide <user_guide/index>
   Gallery <gallery/index>
   About <about>
