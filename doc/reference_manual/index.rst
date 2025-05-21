********************
API Reference Manual
********************

To learn how to use GeoViews, we recommend starting with the
`User guide`_, and then utilizing the online help features within
IPython or Jupyter Notebook to explore further. Each component should support
tab-completion and provide inline help, which is typically sufficient to
understand how to use GeoViews effectively.

For a comprehensive reference to every object in GeoViews, this API documentation
is generated directly from the source code's documentation and declarations.
While it may be verbose due to the inclusion of many inherited or less commonly
used methods, it offers a complete listing of all attributes and methods for each
class, which can be challenging to extract directly from the source code.

--------

Module Structure
________________

GeoViews subpackages
---------------------

`annotators`_
  Helper functions and classes to annotate visual elements.

`data`_
  Data interface classes enabling GeoViews to work with various data types.

`element`_
  Core elements that form the basis of geographic visualizations.

`links`_
  Tools for linking different elements and streams.

`models`_
  Custom models extending GeoViews' capabilities.

`operation`_
  Operations applied to transform existing elements or data structures.

`plotting`_
  Base plotting classes and utilities.

`plotting.bokeh`_
  Bokeh-specific plotting classes and utilities.

`plotting.matplotlib`_
  Matplotlib-specific plotting classes and utilities.

`streams`_
  Stream classes providing interactivity for dynamic maps.

`util`_
  High-level utilities supporting GeoViews functionality.

.. toctree::
   :maxdepth: 2
   :hidden:

   annotators <geoviews.annotators>
   data <geoviews.data>
   element <geoviews.element>
   links <geoviews.links>
   models <geoviews.models>
   operation <geoviews.operation>
   plotting <geoviews.plotting>
   plotting.bokeh <geoviews.plotting.bokeh>
   plotting.matplotlib <geoviews.plotting.mpl>
   streams <geoviews.streams>
   util <geoviews.util>

.. _User guide: ../user_guide/index.html

.. _annotators: geoviews.annotators.html
.. _data: geoviews.data.html
.. _element: geoviews.element.html
.. _links: geoviews.links.html
.. _models: geoviews.models.html
.. _operation: geoviews.operation.html
.. _plotting: geoviews.plotting.html
.. _plotting.bokeh: geoviews.plotting.bokeh.html
.. _plotting.matplotlib: geoviews.plotting.mpl.html
.. _streams: geoviews.streams.html
.. _util: geoviews.util.html
