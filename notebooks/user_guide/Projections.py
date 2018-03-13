import holoviews as hv
import geoviews.feature as gf
from cartopy import crs

"""
The following examples were taken from
http://geo.holoviews.org/user_guide/Projections.html

This script is designed to be run by the python interpreter rather
than in a notebook.
Each function has been designed as a stand-alone example.

Typical modifications when moving from notebook to script include:
    The need to create a renderer with a chosen backend.
    e.g. renderer = hv.renderer('matplotlib')

    plots are saved using render.save method.
    e.g. renderer.save(obj, 'my_filename')
"""


def features_plot():
    """
    global plot with land, ocean, rivers, lakes, borders and coastline
    """

    hv.extension('matplotlib')
    renderer = hv.renderer('matplotlib')
    renderer.size = 400
    features = hv.Overlay([gf.land, gf.ocean, gf.rivers, gf.lakes, gf.borders, gf.coastline])
    renderer.save(features, 'geoviews_features', fmt='png')


def matplotlib_projections():
    """
    various subplots showing the different projections available in
    matplotlib backend (bokeh can only do mercator projection).
    """
    renderer = hv.renderer('matplotlib')
    renderer.size = 200

    projections = [crs.RotatedPole, crs.Mercator, crs.LambertCylindrical, crs.Geostationary,
                   crs.AzimuthalEquidistant, crs.OSGB, crs.EuroPP, crs.Gnomonic, crs.PlateCarree,
                   crs.Mollweide, crs.OSNI, crs.Miller, crs.InterruptedGoodeHomolosine,
                   crs.LambertConformal, crs.SouthPolarStereo, crs.AlbersEqualArea, crs.Orthographic,
                   crs.NorthPolarStereo, crs.Robinson]
    features = hv.Overlay([gf.land, gf.ocean, gf.rivers, gf.lakes, gf.borders, gf.coastline])
    img = hv.Layout([gf.coastline.relabel(group=p.__name__)(plot=dict(projection=p()))
               for p in projections])
    renderer.save(img, 'matplotlib_projections', fmt='png')

def change_projection():
    """
    change projection for a single HoloViews object
    """
    renderer = hv.renderer('matplotlib')
    renderer.size = 200
    features = hv.Overlay([gf.land, gf.ocean, gf.rivers, gf.lakes, gf.borders, gf.coastline])
    img = (features.relabel(group='Mollweide')(plot=dict(projection=crs.Mollweide())) +
            features.relabel(group='Geostationary')(plot=dict(projection=crs.Geostationary())))
    renderer.save(img, 'change_projection', fmt='png')

if __name__ == '__main__':
    features_plot()
    matplotlib_projections()
    change_projection()
