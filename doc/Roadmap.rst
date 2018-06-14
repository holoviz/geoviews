GeoViews Roadmap, as of 6/2018
==============================

GeoViews is under continuous development and improvement, with
priorities determined by user input, the needs of current projects,
and external funding.

Immediate, already funded priorities for 2018 include:

1. **Ongoing maintenance, improved documentation and examples**: As
   always, there are various bugs and usability issues reported on the
   issue tracker, and we will address these as time permits.

2. **Improved imaging, simulation, machine learning, and Earth science
   workflows**: Support for working with image and other
   multidimensional data for visualization and machine-learning
   applications, including on HPC systems.

3. **Improvements to map drawing tools**:
   - Better support for collecting annotations on top of maps
   - other usability improvements

4. **Simpler deployment of large-scale visualizations**: Automatic
   generation of slippy-map tiles for exploration of large datasets
   using standard web servers
   
5. **Rasterization of polygons**: A very common problem in GIS applications
   is combining gridded and geometry data.  As part of ongoing work, datashader
   will gain the ability to rasterize arbitrary geometries by value or simply
   as boolean masks.

Other things we'd like to see in GeoViews or in other supporting tools
in the PyViz ecosystem include:

1. **Integrating 3D earth rendering into GeoViews**: We have a first `prototype
   for a CesiumJS backend for rendering Google-Earth-style plots <http://assets.holoviews.org/demos/HoloViews_CesiumJS.html>`__, 
   but much more work is needed to make it practical for real use.

2. **Toolbox for GIS primitives**: Existing GIS packages provide 
   canned domain-specific functionality, such as computing
   vegetation indexes and other common manipulations of Earth-related
   data. It would be helpful to provide a well-tested collection of
   these common operations built on the PyViz stack so that it can be a
   more "drop-in" replacement for proprietary GIS systems.  Examples
   of desirable functionality:
   
   - Fast geographic indexes for Datashader: NDVI, slope, aspect, hillshade
   - Fast geographic operations for Datashader
       * Zonal statistics for an ROI
           - Percentage area by category
           - Summary stats
       * Hydrology tools
           - Flow accumulation
           - Flow direction
           - Watershed
       * Euclidean distance based on input geometry (lines / polygons / points)
       * Suitability analysis (combining multiple binary aggregates into a yes/no composite)
       * Generate contours from aggregate
       * Calculate viewshed from aggregate
   - Color ramps for showing elevation
   - Bokeh interfaces for external geo data sources (GPX, KML, WMS)
   - Datashader-based WMS Data Server (aggregating an incoming WMS query on demand)

3. Better support for working with remote datasets and remote computation.
   Earth-related datasets tend to be large and remote, and we need to make
   examples of best practice for working with such datasets conveniently and
   with reasonable performance.

4. Integration with other tools like
   [OpenLayers](https://openlayers.org/),
   [Deck.GL](http://uber.github.io/deck.gl), and
   [Leaflet](https://leafletjs.com/).
   
5. Scalable rasterization of raster data, as well as recti- and curvi-linear
   grids, implemented using Dask and Numba in Datashader and exposed in
   HoloViews and GeoViews as fast distributed rendering for Image and
   QuadMesh objects.
   
If any of the functionality above is interesting to you (or you have
ideas of your own!) and can offer help with implementation, please
open an issue on this repository. And if you are lucky enough to be in
a position to fund our developers to work on it, please contact
``sales@anaconda.com``.
