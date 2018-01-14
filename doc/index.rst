********
GeoViews
********


**Geographic visualizations for HoloViews**


.. notebook:: geoviews Homepage.ipynb


Please see the `User Guide <user_guide>`_ for further documentation.


Installation
------------

You can install GeoViews and its other dependencies using conda, many
users will want iris and/or xarray as well::

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
