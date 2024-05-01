from .element import WMTS

# Mapping between patterns to match specified as tuples and tuples containing attributions
_ATTRIBUTIONS = {
    ('openstreetmap',) : (
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    ),
    ('cartodb',) : (
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, '
        '&copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
    ),
    ('cartocdn',) : (
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, '
        '&copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
    ),
    ('stamen', 'png') : ( # to match both 'toner' and 'terrain'
        'Map tiles by <a href="https://stamen.com">Stamen Design</a> / <a href="https://stadiamaps.com">Stadia Maps</a>, '
        'under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
        'Data by <a href="https://openstreetmap.org">OpenStreetMap</a>, '
        'under <a href="https://www.openstreetmap.org/copyright">ODbL</a>.'
    ),
    ('stamen', 'jpg') : (  # watercolor
        'Map tiles by <a href="https://stamen.com">Stamen Design</a> / <a href="https://stadiamaps.com">Stadia Maps</a>, '
        'under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
        'Data by <a href="https://openstreetmap.org">OpenStreetMap</a>, '
        'under <a href="https://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
    ),
    ('wikimedia',) : (
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    ),
    ('arcgis','Terrain') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'USGS, NOAA'
    ),
    ('arcgis','Reference') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Esri, Garmin, GEBCO, NOAA, USGS, and other contributors'
    ),
    ('arcgis','OceanBase') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Esri, Garmin, GEBCO, NOAA, USGS, and other contributors'
    ),
    ('arcgis','OceanReference') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Garmin, USGS, NPS'
    ),
    ('arcgis','Imagery') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Earthstar Geographics'
    ),
    ('arcgis','NatGeo') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'NatGeo, Garmin, HERE, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, Increment P'
    ),
    ('arcgis','USA_Topo') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'NatGeo, i-cubed'
    ),
    ('arcgis','World_Physical_Map') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'US National Park Service'
    ),
    ('arcgis','World_Shaded_Relief') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Esri'
    ),
    ('arcgis','World_Topo_Map') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Esri, HERE, Garmin, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), (c) OpenStreetMap contributors, and the GIS User Community'
    ),
    ('arcgis','World_Dark_Gray_Base') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Esri, HERE, Garmin, (c) OpenStreetMap contributors, and the GIS user community'
    ),
    ('arcgis','World_Dark_Gray_Reference') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Esri, HERE, Garmin, (c) OpenStreetMap contributors, and the GIS user community'
    ),
    ('arcgis','World_Light_Gray_Base') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Esri, HERE, Garmin, (c) OpenStreetMap contributors, and the GIS user community'
    ),
    ('arcgis','World_Light_Gray_Reference') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a>, '
        'Esri, HERE, Garmin, (c) OpenStreetMap contributors, and the GIS user community'
    ),
    ('arcgis','World_Hillshade_Dark') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Esri, Airbus DS, USGS, NGA, NASA, CGIAR, N Robinson, NCEAS, NLS, OS, NMA, Geodatastyrelsen, Rijkswaterstaat, GSA, Geoland, FEMA, Intermap and the GIS user community'
    ),
    ('arcgis','World_Hillshade') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Esri, Airbus DS, USGS, NGA, NASA, CGIAR, N Robinson, NCEAS, NLS, OS, NMA, Geodatastyrelsen, Rijkswaterstaat, GSA, Geoland, FEMA, Intermap and the GIS user community'
    ),
    ('arcgis','Antarctic_Imagery') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Earthstar Geographics'
    ),
    ('arcgis','Arctic_Imagery') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Earthstar Geographics'
    ),
    ('arcgis','Arctic_Ocean_Base') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Esri, Garmin, GEBCO, NOAA NGDC, and other contributors'
    ),
    ('arcgis','Arctic_Ocean_Reference') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Esri, GEBCO, NOAA, National Geographic, Garmin, HERE, Geonames.org, and other contributors'
    ),
    ('arcgis','World_Boundaries_and_Places') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Esri, HERE, Garmin, (c) OpenStreetMap contributors, and the GIS user community'
    ),
    ('arcgis','World_Boundaries_and_Places_Alternate') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Esri, HERE, Garmin, (c) OpenStreetMap contributors, and the GIS user community'
    ),
    ('arcgis','World_Transportation') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Esri, HERE, Garmin, (c) OpenStreetMap contributors'
    ),
    ('arcgis','DeLorme_World_Base_Map') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Garmin'
    ),
    ('arcgis','World_Navigation_Charts') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'East View Cartographic'
    ),
    ('arcgis','World_Street_Map') : (
        '&copy; <a href="http://downloads.esri.com/ArcGISOnline/docs/tou_summary.pdf">Esri</a> '
        'Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China (Hong Kong), Esri Korea, Esri (Thailand), NGCC, (c) OpenStreetMap contributors, and the GIS User Community'
    ),
}

# CartoDB basemaps
CartoDark = WMTS('https://cartodb-basemaps-4.global.ssl.fastly.net/dark_all/{Z}/{X}/{Y}.png', name="CartoDark")
CartoEco = WMTS('http://3.api.cartocdn.com/base-eco/{Z}/{X}/{Y}.png', name="CartoEco")
CartoLight = WMTS('https://cartodb-basemaps-4.global.ssl.fastly.net/light_all/{Z}/{X}/{Y}.png', name="CartoLight")
CartoMidnight = WMTS('http://3.api.cartocdn.com/base-midnight/{Z}/{X}/{Y}.png', name="CartoMidnight")

# Stamen basemaps
StamenTerrain = WMTS('https://tiles.stadiamaps.com/tiles/stamen_terrain/{Z}/{X}/{Y}.png', name="StamenTerrain")
StamenTerrainRetina = WMTS('https://tiles.stadiamaps.com/tiles/stamen_terrain/{Z}/{X}/{Y}@2x.png', name="StamenTerrainRetina")
StamenWatercolor = WMTS('https://tiles.stadiamaps.com/tiles/stamen_watercolor/{Z}/{X}/{Y}.jpg', name="StamenWatercolor")
StamenToner = WMTS('https://tiles.stadiamaps.com/tiles/stamen_toner/{Z}/{X}/{Y}.png', name="StamenToner")
StamenTonerRetina = WMTS('https://tiles.stadiamaps.com/tiles/stamen_toner/{Z}/{X}/{Y}@2x.png', name="StamenTonerRetina")
StamenTonerBackground = WMTS('https://tiles.stadiamaps.com/tiles/stamen_toner_background/{Z}/{X}/{Y}.png', name="StamenTonerBackground")
StamenTonerBackgroundRetina = WMTS('https://tiles.stadiamaps.com/tiles/stamen_toner_background/{Z}/{X}/{Y}@2x.png', name="StamenTonerBackgroundRetina")
StamenLabels = WMTS('https://tiles.stadiamaps.com/tiles/stamen_toner_labels/{Z}/{X}/{Y}.png', name="StamenLabels")
StamenLabelsRetina = WMTS('https://tiles.stadiamaps.com/tiles/stamen_toner_labels/{Z}/{X}/{Y}@2x.png', name="StamenLabelsRetina")

# Esri maps (see https://server.arcgisonline.com/arcgis/rest/services for the full list)
EsriImagery = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg', name="EsriImagery")
EsriNatGeo = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{Z}/{Y}/{X}', name="EsriNatGeo")
EsriUSATopo = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/USA_Topo_Maps/MapServer/tile/{Z}/{Y}/{X}', name="EsriUSATopo")
EsriTerrain = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{Z}/{Y}/{X}', name="EsriTerrain")
EsriReference = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Reference_Overlay/MapServer/tile/{Z}/{Y}/{X}', name="EsriReference")
EsriOceanBase = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{Z}/{Y}/{X}', name="EsriOceanBase")
EsriOceanReference = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{Z}/{Y}/{X}', name="EsriOceanReference")
EsriWorldPhysical = WMTS('https://server.arcgisonline.com/arcgis/rest/services/World_Physical_Map/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldPhysical")
EsriWorldShadedRelief = WMTS('https://server.arcgisonline.com/arcgis/rest/services/World_Shaded_Relief/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldShadedRelief")
EsriWorldTopo = WMTS('https://server.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldTopo")
EsriWorldDarkGrayBase = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldDarkGrayBase")
EsriWorldDarkGrayReference = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldDarkGrayReference")
EsriWorldLightGrayBase = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldLightGrayBase")
EsriWorldLightGrayReference = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldLightGrayReference")
EsriWorldHillshadeDark = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade_Dark/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldHillshadeDark")
EsriWorldHillshade = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldHillshade")
EsriAntarcticImagery = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Polar/Antarctic_Imagery/MapServer/tile/{Z}/{Y}/{X}', name="EsriAntarcticImagery")
EsriArcticImagery = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Polar/Arctic_Imagery/MapServer/tile/{Z}/{Y}/{X}', name="EsriArcticImagery")
EsriArcticOceanBase = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Polar/Arctic_Ocean_Base/MapServer/tile/{Z}/{Y}/{X}', name="EsriArcticOceanBase")
EsriArcticOceanReference = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Polar/Arctic_Ocean_Reference/MapServer/tile/{Z}/{Y}/{X}', name="EsriArcticOceanReference")
EsriWorldBoundariesAndPlaces = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldBoundariesAndPlaces")
EsriWorldBoundariesAndPlacesAlternate = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Reference/World_Boundaries_and_Places_Alternate/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldBoundariesAndPlacesAlternate")
EsriWorldTransportation = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Reference/World_Transportation/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldTransportation")
EsriDelormeWorldBaseMap = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Specialty/DeLorme_World_Base_Map/MapServer/tile/{Z}/{Y}/{X}', name="EsriDelormeWorldBaseMap")
EsriWorldNavigationCharts = WMTS('https://server.arcgisonline.com/arcgis/rest/services/Specialty/World_Navigation_Charts/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldNavigationCharts")
EsriWorldStreetMap = WMTS('https://server.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{Z}/{Y}/{X}', name="EsriWorldStreetMap")
ESRI = EsriImagery # For backwards compatibility with gv 1.5


# Miscellaneous
OSM = WMTS('https://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png', name="OSM")
OpenTopoMap = WMTS('https://a.tile.opentopomap.org/{Z}/{X}/{Y}.png', name="OpenTopoMap")

tile_sources = {k: v for k, v in locals().items() if isinstance(v, WMTS) and k != 'ESRI' and "Stamen" not in k}

stamen_sources = [k for k, v in locals().items() if isinstance(v, WMTS) and "Stamen" in k]
