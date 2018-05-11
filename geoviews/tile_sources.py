from .element import WMTS

# Mapping between patterns to match specified as tuples and tuples containing attributions
_ATTRIBUTIONS = {
    ('openstreetmap',)      : (
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    ),
    ('cartodb') : (
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors,'
        '&copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
    ),
    ('cartocdn') : (
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors,'
        '&copy; <a href="https://cartodb.com/attributions">CartoDB</a>'
    ),
    ('stamen', 'terrain'): (
        'Map tiles by <a href="https://stamen.com">Stamen Design</a>, '
        'under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
        'Data by <a href="https://openstreetmap.org">OpenStreetMap</a>, '
        'under <a href="https://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
    ),
    ('stamen', 'toner'): (
        'Map tiles by <a href="https://stamen.com">Stamen Design</a>, '
        'under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. '
        'Data by <a href="https://openstreetmap.org">OpenStreetMap</a>, '
        'under <a href="https://www.openstreetmap.org/copyright">ODbL</a>.'
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
StamenWatercolor = WMTS('http://c.tile.stamen.com/watercolor/{Z}/{X}/{Y}.jpg')
StamenToner = WMTS('http://tile.stamen.com/toner/{Z}/{X}/{Y}.png')
StamenTonerBackground = WMTS('http://tile.stamen.com/toner-background/{Z}/{X}/{Y}.png')
StamenLabels = WMTS('http://tile.stamen.com/toner-labels/{Z}/{X}/{Y}.png')

# Miscellaneous
OSM = WMTS('http://c.tile.openstreetmap.org/{Z}/{X}/{Y}.png')
ESRI = WMTS('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{Y}/{X}.jpg')
Wikipedia = WMTS('https://maps.wikimedia.org/osm-intl/{Z}/{X}/{Y}@2x.png')

tile_sources = {k: v for k, v in locals().items() if isinstance(v, WMTS)}
