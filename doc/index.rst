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

You can install GeoViews and its dependencies using conda::

    conda install -c pyviz geoviews

Alternatively you can install the geoviews-core package, which
only installs the minimal dependencies required to run geoviews::

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

GeoViews itself is also installable using ``pip``, but to do that you
will first need to have installed the `dependencies of cartopy <http://scitools.org.uk/cartopy/docs/latest/installing.html#requirements>`_,
or else have set up your system to be able to build them.

Using GeoViews offline
======================

Under the hood, GeoViews features simply wrap ``cartopy`` features, so it's a matter of properly
configuring ``cartopy`` ahead of time.

1. Create a new cartopy environment (or use an existing one)::

    conda create -n cartopy_env python=3.10

2. Install the required packages::

    conda install -c conda-forge geoviews cartopy cartopy_offlinedata

3. Verify offline shapefiles were downloaded::

    import cartopy

    data_dir = cartopy.config["pre_existing_data_dir"]
    shapefiles = data_dir / "shapefiles" / "natural_earth" / "cultural"
    list(shapefiles.glob("*"))

4. Test GeoViews offline (toggle internet off)::

    import geoviews as gv
    from bokeh.resources import INLINE

    gv.extension("bokeh")

    coastline = gv.feature.coastline()
    borders = gv.feature.borders()
    world = (coastline * borders).opts(global_extent=True)

    gv.save(world, "world.html", resources=INLINE)

Please ensure to set ``resources=INLINE`` if the machine you're using is completely
offline and you intend to view the output on that machine.
Failure to do so will result in the HTML file appearing empty when opened.

If you wish to change the default data directory, follow these steps:

1. Create a new directory and move the data::

    import cartopy

    new_data_dir = Path("~/.cartopy").expanduser()
    new_data_dir.mkdir(exist_ok=True)

    data_dir = Path(cartopy.config["pre_existing_data_dir"])
    data_dir.rename(new_data_dir / "cartopy")

2. Point to the new data directory within the script::

    import cartopy
    import geoviews as gv
    from bokeh.resources import INLINE

    cartopy.config["pre_existing_data_dir"] = "~/.cartopy/cartopy"

    gv.extension("bokeh")

    coastline = gv.feature.coastline()
    borders = gv.feature.borders()
    world = (coastline * borders).opts(global_extent=True)

    gv.save(world, "world.html", resources=INLINE)

3. Or set an environment variable ``CARTOPY_DATA_DIR``::

    export CARTOPY_DATA_DIR="$HOME/.cartopy/cartopy"

Please note using tilde (``~``) in the environment variable will not work.

.. toctree::
   :hidden:
   :maxdepth: 2

   Home <self>
   User Guide <user_guide/index>
   Gallery <gallery/index>
   Topics <topics>
   Releases <releases>
   About <about>
