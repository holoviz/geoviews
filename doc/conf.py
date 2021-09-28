# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'GeoViews'
authors = u'HoloViz Developers'
copyright = u'2018-2019 ' + authors
description = 'Geographic visualizations for HoloViews.'

import geoviews
version = release = str(geoviews.__version__)

html_static_path += ['_static']

html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    "github_url": "https://github.com/holoviz/geoviews",
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/HoloViews",
            "icon": "fab fa-twitter-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.holoviz.org/",
            "icon": "fab fa-discourse",
        }
    ]
}

extensions += [
    'sphinx.ext.napoleon',
    'nbsite.gallery',
    'sphinx_copybutton',
]
napoleon_numpy_docstring = True

templates_path = ['_templates']

nbsite_gallery_conf = {
    'backends': ['bokeh', 'matplotlib'],
    'galleries': {
        'gallery': {'title': 'Gallery'}
    },
    'github_org': 'holoviz',
    'github_project': 'geoviews'
}

extensions += ['nbsite.gallery']

html_context.update({
    "last_release": f"v{'.'.join(geoviews.__version__.split('.')[:3])}",
    "github_user": "holoviz",
    "github_repo": "geoviews",
    "google_analytics_id": "UA-154795830-2",
})
