from .element import WMTS

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
