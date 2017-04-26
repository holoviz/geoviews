.. GeoViews documentation master file

.. raw:: html
  :file: latest_news.html

Introduction
____________

.. notebook:: geoviews Homepage.ipynb

Installation
------------

You can then install GeoViews and its other dependencies using conda,
many users will want iris and/or xarray as well::

   conda install -c conda-forge -c ioam holoviews geoviews
   # (Optional)
   conda install xarray
   conda install -c conda-forge iris

You can now switch to your preferred working directory, grab a copy of
the notebooks to run locally, and run them using the Jupyter notebook::

   cd ~
   python -c 'import geoviews; geoviews.examples("geoviews-examples",include_data=True)'
   cd geoviews-examples
   jupyter notebook

------------

Support
_______

GeoViews was developed through a collaboration between
`Continuum Analytics <https://continuum.io>`_ and the `Met Office
<http://www.metoffice.gov.uk>`_.  GeoViews is completely `open source
<https://github.com/ioam/geoviews>`_, available under a BSD license
freely for both commercial and non-commercial use.  Please file
bug reports and feature requests on our
`github site <https://github.com/ioam/geoviews/issues>`_.

.. toctree::
   :titlesonly:
   :hidden:
   :maxdepth: 2

   Home <self>
   Projections <Projections>
   Geometries <Geometries>
   Working with Gridded Data I <Gridded_Datasets_I>
   Working with Gridded Data II <Gridded_Datasets_II>
   Working with Bokeh <Working_with_Bokeh>
   Github source <https://github.com/ioam/geoviews>
