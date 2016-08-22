from cartopy import feature as cf

from .element import Feature

borders   = Feature(cf.BORDERS, group='Borders')
coastline = Feature(cf.COASTLINE, group='Coastline')
land      = Feature(cf.LAND, group='Land')
lakes     = Feature(cf.LAKES, group='Lakes')
ocean     = Feature(cf.OCEAN, group='Ocean')
rivers    = Feature(cf.RIVERS, group='Rivers')
