Releases
========

Version 1.9.3
-------------

This release contains a few bug fixes and improvements, and adds compatibility to Shapely 1.8 and the upcoming version 2.0. Thanks to @philippjfr, @maximlt and @ahuang11 for contributing to this release.

Bug fixes and minor improvements:

- Add missing _process_msg method to GeoPolyEditCallback (`#539 <https://github.com/holoviz/geoviews/pull/539>`_)
- Accept lowercase xmin/ymin/xmax/ymax in WMTS URL templates (`#542 <https://github.com/holoviz/geoviews/pull/542>`_)
- Support GeoDataframe with a geometry column not named geometry (`#545 <https://github.com/holoviz/geoviews/pull/545>`_)
- Add opentopomap as a tile source (`#514 <https://github.com/holoviz/geoviews/pull/514>`_)

Compatibility:

- Adapt to shapely 1.8.0 and 2.0 (`#543 <https://github.com/holoviz/geoviews/pull/543>`_)

Docs improvements:

- Update the CSS of links (`#544 <https://github.com/holoviz/geoviews/pull/544>`_)


Version 1.9.2
-------------

Minor release by @philippjfr for Bokeh 2.4 compatibility:

- Rebuild extensions for Bokeh >=2.4 (`#525 <https://github.com/holoviz/geoviews/pull/525>`_)
- Require cartopy>=0.18 to match conda-forge recipe
- Fix compatibility with upcoming HoloViews 2.0
- Switch website to pydata_sphinx_theme (`#528 <https://github.com/holoviz/geoviews/pull/528>`_)


Version 1.9.1
-------------

This micro-release fixes the bundling and deployment of geoviews.js to NPM but otherwise has no contents.


Version 1.9.0
-------------

This GeoViews release primarily provides compatibility with the latest releases of Cartopy (0.18), Bokeh (2.3), HoloViews (1.14.x) and fixes a number of other issues.

Features:

- Add utility to download tile RGB (`#458 <https://github.com/holoviz/geoviews/pull/458>`_)

Compatibility:

- Compatibility with Bokeh 2.3 (`#487 <https://github.com/holoviz/geoviews/pull/487>`_)
- Compatibility for regridding with latest xesmf (`#488 <https://github.com/holoviz/geoviews/pull/488>`_)
- Compatibility with HoloViews 1.14.x for resampling operation and stream callback (`#488 <https://github.com/holoviz/geoviews/pull/488>`_)
- Compatibility with latest Cartopy 0.18 (`#488 <https://github.com/holoviz/geoviews/pull/488>`_)

Bug fixes:

- Allow using geopandas interface without using geometry column (`#464 <https://github.com/holoviz/geoviews/pull/464>`_)
- Fix Hover tooltip projection (`#490 <https://github.com/holoviz/geoviews/pull/490>`_)
- Use the set geometry column on Geopandas DataFrames (`#489 <https://github.com/holoviz/geoviews/pull/489>`_)
- Fix xesmf regridding file_pattern parameter (`#491 <https://github.com/holoviz/geoviews/pull/491>`_)


Version 1.8.2
-------------

Minor bugfix release. Includes contributions from: @philippjfr

Bug fixes and minor improvements:

- Bump geoviews.js version and bokeh requirements (`#473 <https://github.com/holoviz/geoviews/pull/473>`_)
- Handle proj4.js API change in Hover formatter (`#472 <https://github.com/holoviz/geoviews/pull/472>`_)


Version 1.8.1
-------------

This fixes some minor incompatibilities between latest HoloViews and the Iris data interface in GeoViews.

- Updated Iris interface for compatibility with HoloViews 1.13.x (`#453 <https://github.com/holoviz/geoviews/pull/453>`_)

Version 1.8.0
-------------

This release makes introduces no actual changes on top of version 1.7.0, it simply adds a dependency on bokeh>=2.0, which also means that this is the first version that requires Python 3.

- Compatibility with Bokeh 2.0 (`#449 <https://github.com/holoviz/geoviews/pull/449>`_)

Version 1.7.0
-------------

This release adds some major features to HoloViews and adds compatibility for HoloViews 1.13.0. This is also the last release with support for Python 2. Many thanks for the many people who contributed by filing issues and our contributors including @ceball, @jsignell, @ahuang11, @jbednar and @philippjfr.

Features:


* Added geographic projection awareness to ``hv.annotate`` function (`#377 <https://github.com/holoviz/geoviews/pull/377>`_, `#419 <https://github.com/holoviz/geoviews/pull/419>`_)
* Rewrote geometry interfaces such as geopandas to conform to new HoloViews geometry protocol (`#407 <https://github.com/holoviz/geoviews/pull/407>`_)
* Implement consistent .geom method on geometry types (e.g. Path, Polygons, Points) (`#424 <https://github.com/holoviz/geoviews/pull/424>`_)
* Add new `Rectangles` and `Segments` elements (`#377 <https://github.com/holoviz/geoviews/pull/377>`_)

Bug fixes:


* Allow updating user defined HoverTool instances (`#440 <https://github.com/holoviz/geoviews/pull/440>`_)
* Fix for ticks fontsize in matplotlib backend (`#402 <https://github.com/holoviz/geoviews/pull/402>`_)
* Fix for xaxis/yaxis='bare' option in matplotlib backend (`#401 <https://github.com/holoviz/geoviews/pull/401>`_)

Compatibility:


* Compatibility with HoloViews 1.13.0 (`#429 <https://github.com/holoviz/geoviews/pull/429>`_, `#430 <https://github.com/holoviz/geoviews/pull/430>`_)

Version 1.6.6
-------------

This is a minor release with a small number of bug fixes. Thanks to @nickhand, @philippjfr and @jsignell for contributing to this release.


* Ensure that projecting QuadMesh does not drop options (`#367 <https://github.com/holoviz/geoviews/pull/367>`_)
* Fix handling of pyproj strings (`#376 <https://github.com/holoviz/geoviews/pull/376>`_)
* Disable ``fixed_bounds`` to avoid bug when zooming in bokeh (`#390 <https://github.com/holoviz/geoviews/pull/390>`_)
* Add support for geometry columns other than 'geometry' on geopandas DataFrames (`#391 <https://github.com/holoviz/geoviews/pull/391>`_)
* Fixed handling of pyproj dependency (`#392 <https://github.com/holoviz/geoviews/pull/392>`_)

Version 1.6.5
-------------

Minor bugfix release. Includes contributions from @philippjfr:

Bug fixes and minor improvements:


* Fixed issues with target extents in project_image (`#365 <https://github.com/holoviz/geoviews/pull/365>`_)

Version 1.6.4
-------------

Minor bugfix release. Includes contributions from @philippjfr, @ahuang11, @zassa, and @ceball 

Bug fixes and minor improvements:


* Ensure that gridline labels are only drawn once (`#364 <https://github.com/holoviz/geoviews/pull/364>`_)
* Compatibility with latest HoloViews data interface (`#363 <https://github.com/holoviz/geoviews/pull/363>`_)
* Add grid labels (`#351 <https://github.com/holoviz/geoviews/pull/351>`_)
* Hardcode the OSM tile source to https (`#333 <https://github.com/holoviz/geoviews/pull/333>`_)
* Fix hover formatting for Mercator coordinates (`#358 <https://github.com/holoviz/geoviews/pull/358>`_)

Version 1.6.3
-------------

Minor release, mostly bugfixes. Includes contributions from @philippjfr, @ahuang11, and @rsignell-usgs.

New features:


* Add geo features for US states (`#312 <https://github.com/holoviz/geoviews/pull/312>`_)
* Add ESRI Ocean tile layers (`#320 <https://github.com/holoviz/geoviews/pull/320>`_)

Bug fixes and minor improvements:


* Add dtype methods to geometry interfaces (`#345 <https://github.com/holoviz/geoviews/pull/345>`_)
* Ensure that Line Shape is not filled in matplotlib (`#326 <https://github.com/holoviz/geoviews/pull/326>`_)
* Avoid zooming in beyond tile/axis resolution (`#325 <https://github.com/holoviz/geoviews/pull/325>`_)
* Fix gridlines for gv matplotlib overlay (`#308 <https://github.com/holoviz/geoviews/pull/308>`_)

Version 1.6.2
-------------

Minor release, mostly bugfixes. Includes contributions from @philippjfr.

New feature:


* Add adaptive geometry resampling operation, allowing working with large shape files interactively, increasing their resolution when zooming in (`#282 <https://github.com/holoviz/geoviews/pull/282>`_)

Bug fixes and minor improvements:


* Fixed img project if src and target projection are equal (`#288 <https://github.com/holoviz/geoviews/pull/288>`_)
* Added plotting backend load hooks (`#286 <https://github.com/holoviz/geoviews/pull/286>`_)
* Do not import regrid operations by default
* Fixed re-initialization of backend (`#284 <https://github.com/holoviz/geoviews/pull/284>`_)
* Improved handling of non-default central longitudes (`#281 <https://github.com/holoviz/geoviews/pull/281>`_)
* Small fix for Path longitude wrapping (`#279 <https://github.com/holoviz/geoviews/pull/269>`_)

Version 1.6.2
-------------

Includes contributions from @ahuang11 (unlimit vdims) and @philippjfr.

Bug fixes and minor improvements:


* Unlimit the vdims for various elements (`#253 <https://github.com/holoviz/geoviews/pull/253>`_)
* Improve handling of geopandas and empty geometries (`#278 <https://github.com/holoviz/geoviews/pull/278>`_)
* Updated opts syntax in gallery examples (`#277 <https://github.com/holoviz/geoviews/pull/277>`_)
* Fixed bugs projecting ``Graphs`` (`#276 <https://github.com/holoviz/geoviews/pull/276>`_)
* Ensure backend is initialized on import (`#275 <https://github.com/holoviz/geoviews/pull/275>`_)
* Added ``__call__`` method to tile sources, to restore constructor-like behavior from previous versions (`#274 <https://github.com/holoviz/geoviews/pull/274>`_)

Version 1.6.0
-------------

This is a major release with a number of important enhancements and bug fixes:

Features:


* Complete overhaul of geometry handling including support for geometry with holes and geometry dictionary interface (`#244](https://github.com/holoviz/geoviews/pull/244), #249 <https://github.com/holoviz/geoviews/pull/249>`_)
* Support for holoviews FreehandDraw stream (`#219 <https://github.com/holoviz/geoviews/pull/219>`_)
* Add ``gv.load_tiff`` and ``gv.RGB.load_tiff`` helpers (`#221](https://github.com/holoviz/geoviews/pull/221), #233 <https://github.com/holoviz/geoviews/pull/233>`_)
* Added support for holoviews padding option (`#228 <https://github.com/holoviz/geoviews/pull/228>`_)

Enhancements:


* Drop bokeh save tool when tile source is used (`#257 <https://github.com/holoviz/geoviews/pull/257>`_)
* Compatibility with cartopy 0.17 (`#254 <https://github.com/holoviz/geoviews/pull/254>`_)

Bug fixes:


* Improved handling of Point geometries in geopandas dataframe (`#204 <https://github.com/holoviz/geoviews/pull/204>`_) 
* Fixes for projecting draw tool data (`#205 <https://github.com/holoviz/geoviews/pull/205>`_)
* Improvements and fixes for handling of QuadMesh projections (`#250 <https://github.com/holoviz/geoviews/pull/250>`_)
* Fixes for Image longitude wrapping (`#260 <https://github.com/holoviz/geoviews/pull/260>`_)

Version 1.5.1
-------------

This is a bug fix release which includes a number of important fixes and enhancements.

Enhancements:


* Geopandas interface now supports point geometries (`#186 <https://github.com/holoviz/geoviews/pull/186>`_)
* Geopandas data now supported in the ``.to`` conversion API (`#186 <https://github.com/holoviz/geoviews/pull/186>`_)

Fixes:


* Fixed some issues to do with tile source attributions (`#176 <https://github.com/holoviz/geoviews/pull/176>`_)
* Fixed bug projecting rectilinear QuadMesh (`#178 <https://github.com/holoviz/geoviews/pull/178>`_)
* Improvements to path/polygon projection and clipping (`#179 <https://github.com/holoviz/geoviews/pull/179>`_)

Version 1.5.0
-------------

Major feature:


* The bokeh backend now supports arbitrary geographic projections, no longer just Web Mercator (`#170 <https://github.com/holoviz/geoviews/pull/170>`_)

New components:


* 
  Added `Graph element <http://holoviews.org/reference/elements/bokeh/Graph.html>`_ to plot networks of connected nodes (`#115 <https://github.com/holoviz/geoviews/pull/115>`_)

* 
  Added `TriMesh element <http://holoviews.org/reference/elements/bokeh/TriMesh.html>`_ and datashading operation to plot small and large irregular triangular meshes (`#115 <https://github.com/holoviz/geoviews/pull/115>`_)

* 
  Added `QuadMesh element <http://holoviews.org/reference/elements/bokeh/QuadMesh.html>`_ and datashading operation to plot small and large, irregular rectilinear and curvilinear meshes (`#116 <https://github.com/holoviz/geoviews/pull/116>`_)

* 
  Added `VectorField element <http://holoviews.org/reference/elements/bokeh/VectorField.html>`_ and datashading operation to plot small and large quiver plots and other collections of vectors (`#122 <https://github.com/holoviz/geoviews/pull/122>`_)

* 
  Added `HexTiles element <http://holoviews.org/reference/elements/bokeh/HexTiles.html>`_ to plot data binned into a hexagonal grid (`#147 <https://github.com/holoviz/geoviews/pull/147>`_)

* 
  Added `Labels element <http://holoviews.org/reference/elements/bokeh/Labels.html>`_ to plot a large number of text labels at once (as data rather than as annotations) (`#147 <https://github.com/holoviz/geoviews/pull/147>`_)

New features:


* 
  Hover tool now supports displaying geographic coordinates as longitude and latitude (`#158 <https://github.com/holoviz/geoviews/pull/158>`_) 

* 
  Added a new ``geoviews.tile_sources`` module with a predefined set of tile sources (`#165 <https://github.com/holoviz/geoviews/pull/165>`_)

* 
  Wrapped the xESMF library as a regridding and interpolation operation for rectilinear and curvilinear grids (`#127 <https://github.com/holoviz/geoviews/pull/127>`_)

* 
  HoloViews operations including ``datashade`` and ``rasterize`` now retain geographic ``crs`` coordinate system (`#118 <https://github.com/holoviz/geoviews/pull/118>`_)

Enhancements:


* Overhauled documentation and added a gallery (`#121 <https://github.com/holoviz/geoviews/pull/121>`_)

Version 1.4.3
-------------

Enhancements:


* Ensured that HoloViews operations such as datashade, aggregate and regrid do not drop the coordinate reference system on the input element (`#118 <https://github.com/holoviz/geoviews/pull/118>`_)
* Unified WMTS support across backends, bokeh and matplotlib now support rendering ``{X}_{Y}_{Z}`` based web tiles (`#120 <https://github.com/holoviz/geoviews/pull/120>`_)
* Handle projecting of empty Elements (`#131 <https://github.com/holoviz/geoviews/pull/131>`_)
* Set Image element NaN coloring to transparent (`#136 <https://github.com/holoviz/geoviews/pull/136/commits/f1f29607079f1f86bce56187dd7a98ca2a1d9eff>`_)
* Overhauled website with new theme (`#106 <https://github.com/holoviz/geoviews/pull/106>`_)

Version 1.4.2
-------------

Version 1.4.1
-------------

Version 1.4.0
-------------


* Allow specifying WMTS element with just the URL (`#89 <https://github.com/holoviz/geoviews/pull/89>`_)
* Added GeoPandas interface to plot geometries more easily (`#88 <https://github.com/holoviz/geoviews/pull/88>`_)
* Added further projection operations allowing most geographic element types to be explicitly projected (`#88 <https://github.com/holoviz/geoviews/pull/88>`_)
* Enabled MercatorTicker on geographic bokeh plots ensuring axes are labelled with latitudes and longitudes (`#64 <https://github.com/holoviz/geoviews/pull/64>`_) 

Version 1.3.2
-------------

This is a minor release reapplying a fix which was accidentally reverted in 1.3.1:


* The WMTS Element now accepts a tile source URL directly for the bokeh backend (PR #83)

Version 1.3.1
-------------

This is a minor release with one small improvements:


* The WMTS Element now accepts a tile source URL directly for the bokeh backend (`PR #83 <https://github.com/holoviz/geoviews/pull/83>`_)

Version 1.3.0
-------------

This release is mostly a compatibility release for HoloViews 1.8. It includes a small number of significant fixes and changes:


* Introduces a general ``project`` operation to project most Element types from one ``crs`` to another (`#69 <https://github.com/holoviz/geoviews/pull/69>`_)
* Added a ``gv.RGB`` Element type useful for representing datashader aggregates and particularly loading GeoTiffs with xarray (`#75 <https://github.com/holoviz/geoviews/pull/75>`_)
* All geoviews geographic Elements declare a ``crs``, which defaults to ``PlateCarree()`` (`#76 <https://github.com/holoviz/geoviews/pull/76>`_)
* Fix for compatibility with HoloViews 1.8 (`#77 <https://github.com/holoviz/geoviews/pull/77>`_)

Version 1.2.0
-------------

This is a minor release mostly to maintain compatibility with the recently released HoloViews 1.7.0.

Features:


* Added ``project_shape`` operations (`c6c5ce <https://github.com/holoviz/geoviews/commit/c6c5ce261aa725853e00094fbe59ff3650ad1e19>`_)
* The ``Shape.from_records`` function now supports ``drop_missing`` option.  #63
* Compatibility with HoloViews (`#59 <https://github.com/holoviz/geoviews/pull/59>`_, `#60 <https://github.com/holoviz/geoviews/pull/60>`_)
* Bokeh box_zoom tool now matches aspect on geographic plots (`c6c41a9 <https://github.com/holoviz/geoviews/commit/c6c41a979dca928c83d74c3773df458840832907>`_)

Bug fixes:


* Fix for ``Shape`` Element colormapping (`#58 <https://github.com/holoviz/geoviews/pull/58>`_)
* Geographic objects did not inherit ``crs`` on clone (`df0ba8 <https://github.com/holoviz/geoviews/commit/df0ba893e273e8a143d78419f6491c27ed814fe5>`_)

Version 1.1.0
-------------

Minor release to improve usability:


* Improved layouts, reducing whitespace around non-square plots
* Added ``geoviews.features`` module for simple access to cartopy Features.
* Improved tutorials
* Added ``gv.Dataset`` class to simplify keeping track of coordinate systems

Version 1.0.0
-------------

First stable version, with support for matplotlib and bokeh (web Mercator projection only). Requires HoloViews 1.6+ to be able to use data from xarray or iris.
