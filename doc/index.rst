********
GeoViews
********

.. raw:: html

   <div style="width: 65%; float:left">

	 
**Geographic visualizations for HoloViews**

Project is an `open-source
<https://github.com/ioam/holoviews/blob/master/LICENSE.txt>`_ Python
library for something something something something and something
more.

The `User Guide <user_guide>`_...


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


.. raw:: html
  
   </div>


.. raw:: html
  :file: latest_news.html


.. raw:: html

   <hr width='100%'></hr>
	 
   <div>
   <div >
     <a href="http://holoviews.org/gallery/demos/bokeh/iris_splom_example.html">
       <img src="http://holoviews.org/_images/iris_splom_example.png" width='20%'>    </img> </a>
     <a href="http://holoviews.org/getting_started/Gridded_Datasets.html">
       <img src="http://assets.holoviews.org/collage/cells.png" width='22%'> </img>  </a>
     <a href="http://holoviews.org/gallery/demos/bokeh/scatter_economic.html">
       <img src="http://holoviews.org/_images/scatter_economic.png" width='43%'> </img>    </a>
   </div>

   <div >
     <a href="http://holoviews.org/gallery/demos/bokeh/square_limit.html">
       <img src="http://holoviews.org/_images/square_limit.png" width='20%'> </a>
     <a href="http://holoviews.org/gallery/demos/bokeh/bars_economic.html">
       <img src="http://holoviews.org/_images/bars_economic.png" width='20%'> </a>
     <a href="http://holoviews.org/gallery/demos/bokeh/texas_choropleth_example.html">
       <img src="http://holoviews.org/_images/texas_choropleth_example.png"    width='20%'> </a>
     <a href="http://holoviews.org/gallery/demos/bokeh/verhulst_mandelbrot.html">
       <img src="http://holoviews.org/_images/verhulst_mandelbrot.png" width='20%'>    </a>
   </div>
   <div >
       <a href="http://holoviews.org/gallery/demos/bokeh/dropdown_economic.html">
         <img src="http://assets.holoviews.org/collage/dropdown.gif" width='31%'> </a>
       <a href="http://holoviews.org/gallery/demos/bokeh/dragon_curve.html">
         <img src="http://assets.holoviews.org/collage/dragon_fractal.gif" width='26%'> </a>
       <a href="http://holoviews.org/gallery/apps/bokeh/nytaxi_hover.html">
         <img src="http://assets.holoviews.org/collage/ny_datashader.gif" width='31%'> </a>
   </div>
   </div>
   <hr width='100%'></hr>

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
   About <about>
