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
    ('stamen', 'com/t') : ( # to match both 'toner' and 'terrain'
        'Map tiles by <a href="https://stamen.com">Stamen Design</a>, '
        'under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
        'Data by <a href="https://openstreetmap.org">OpenStreetMap</a>, '
        'under <a href="https://www.openstreetmap.org/copyright">ODbL</a>.'
    ),
    ('stamen', 'watercolor') : (
        'Map tiles by <a href="https://stamen.com">Stamen Design</a>, '
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
    )
}

# CartoDB basemaps
CartoDark = WMTS('https://cartodb-basemaps-4.global.ssl.fastly.net/dark_all/{Z}/{X}/{Y}.png', name="CartoDark")
CartoEco = WMTS('http://3.api.cartocdn.com/base-eco/{Z}/{X}/{Y}.png', name="CartoEco")
CartoLight = WMTS('https://cartodb-basemaps-4.global.ssl.fastly.net/light_all/{Z}/{X}/{Y}.png', name="CartoLight")
CartoMidnight = WMTS('http://3.api.cartocdn.com/base-midnight/{Z}/{X}/{Y}.png', name="CartoMidnight")

# Stamen basemaps
StamenTerrain = WMTS('http://tile.stamen.com/terrain/{Z}/{X}/{Y}.png', name="StamenTerrain")
StamenTerrainRetina = WMTS('http://tile.stamen.com/terrain/{Z}/{X}/{Y}@2x.png', name="StamenTerrainRetina")
StamenWatercolor = WMTS('http://tile.stamen.com/watercolor/{Z}/{X}/{Y}.jpg', name="StamenWatercolor")
StamenToner = WMTS('http://tile.stamen.com/toner/{Z}/{X}/{Y}.png', name="StamenToner")
StamenTonerBackground = WMTS('http://tile.stamen.com/toner-background/{Z}/{X}/{Y}.png', name="StamenTonerBackground")
StamenLabels = WMTS('http://tile.stamen.com/toner-labels/{Z}/{X}/{Y}.png', name="StamenLabels")

# Esri maps (see https://server.arcgisonline.com/arcgis/rest/services for the full list)
EsriImagery = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg', name="EsriImagery")
EsriNatGeo = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{Z}/{Y}/{X}', name="EsriNatGeo")
EsriUSATopo = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/USA_Topo_Maps/MapServer/tile/{Z}/{Y}/{X}', name="EsriUSATopo")
EsriTerrain = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{Z}/{Y}/{X}', name="EsriTerrain")
EsriReference = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Reference_Overlay/MapServer/tile/{Z}/{Y}/{X}', name="EsriReference")
EsriOceanBase = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{Z}/{Y}/{X}', name="EsriOceanBase")
EsriOceanReference = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{Z}/{Y}/{X}', name="EsriOceanReference")
ESRI = EsriImagery # For backwards compatibility with gv 1.5


# Miscellaneous
OSM = WMTS('https://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png', name="OSM")
OpenTopoMap = WMTS('https://a.tile.opentopomap.org/{Z}/{X}/{Y}.png', name="OpenTopoMap")

def __getattr__(name):
    if name == "Wikipedia":
        from ._warnings import deprecated
        deprecated("1.11", "Wikipedia", "OSM")
        return WMTS('https://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png', name="Wikipedia")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


tile_sources = {k: v for k, v in locals().items() if isinstance(v, WMTS) and k != 'ESRI'}
