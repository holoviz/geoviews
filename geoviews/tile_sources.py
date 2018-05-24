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
CartoDark = WMTS('https://cartodb-basemaps-4.global.ssl.fastly.net/dark_all/{Z}/{X}/{Y}.png')
CartoEco = WMTS('http://3.api.cartocdn.com/base-eco/{Z}/{X}/{Y}.png')
CartoLight = WMTS('https://cartodb-basemaps-4.global.ssl.fastly.net/light_all/{Z}/{X}/{Y}.png')
CartoMidnight = WMTS('http://3.api.cartocdn.com/base-midnight/{Z}/{X}/{Y}.png')

# Stamen basemaps
StamenTerrain = WMTS('http://tile.stamen.com/terrain/{Z}/{X}/{Y}.png')
StamenTerrainRetina = WMTS('http://tile.stamen.com/terrain/{Z}/{X}/{Y}@2x.png')
StamenWatercolor = WMTS('http://tile.stamen.com/watercolor/{Z}/{X}/{Y}.jpg')
StamenToner = WMTS('http://tile.stamen.com/toner/{Z}/{X}/{Y}.png')
StamenTonerBackground = WMTS('http://tile.stamen.com/toner-background/{Z}/{X}/{Y}.png')
StamenLabels = WMTS('http://tile.stamen.com/toner-labels/{Z}/{X}/{Y}.png')

# Esri maps (see https://server.arcgisonline.com/arcgis/rest/services for the full list)
EsriImagery = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg')
EsriNatGeo = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{Z}/{Y}/{X}')
EsriUSATopo = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/USA_Topo_Maps/MapServer/tile/{Z}/{Y}/{X}')
EsriTerrain = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{Z}/{Y}/{X}')
EsriReference = WMTS('http://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Reference_Overlay/MapServer/tile/{Z}/{Y}/{X}')
ESRI = EsriImagery # For backwards compatibility with gv 1.5


# Miscellaneous
OSM = WMTS('http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png')
Wikipedia = WMTS('https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png')


tile_sources = {k: v for k, v in locals().items() if isinstance(v, WMTS) and k != 'ESRI'}
