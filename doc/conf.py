# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = 'GeoViews'
authors = 'HoloViz Developers'
copyright = '2018 ' + authors
description = 'Geographic visualizations for HoloViews.'

import geoviews
version = release = base_version(geoviews.__version__)

html_static_path += ['_static']

html_css_files += [
    'custom.css'
]

html_theme = 'pydata_sphinx_theme'
html_logo = "_static/logo_horizontal.png"
html_favicon = "_static/favicon.ico"

html_theme_options = {
    "github_url": "https://github.com/holoviz/geoviews",
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://twitter.com/HoloViews",
            "icon": "fa-brands fa-twitter-square",
        },
        {
            "name": "Discourse",
            "url": "https://discourse.holoviz.org/c/geoviews",
            "icon": "fa-brands fa-discourse",
        },
        {
            "name": "Discord",
            "url": "https://discord.gg/AXRHnJU6sP",
            "icon": "fa-brands fa-discord",
        },
    ],
    "pygment_dark_style": "material"
}

extensions += [
    'nbsite.gallery',
    'nbsite.analytics',
    'sphinx_reredirects',
]

myst_enable_extensions = ["colon_fence", "deflist"]

napoleon_numpy_docstring = True

nbsite_analytics = {
    'goatcounter_holoviz': True,
}

redirects = {
    'topics/index': 'https://examples.holoviz.org',
}

nbsite_gallery_conf = {
    'github_org': 'holoviz',
    'github_project': 'geoviews',
    'backends': ['bokeh', 'matplotlib'],
    'galleries': {
        'gallery': {
            'title': 'Gallery'
        }
    },
    'thumbnail_url': 'https://assets.holoviz.org/geoviews/thumbnails',
}

html_context.update({
    "last_release": f"v{release}",
    "github_user": "holoviz",
    "github_repo": "geoviews",
    "default_mode": "light"
})

# Override the Sphinx default title that appends `documentation`
html_title = f'{project} v{version}'
