# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'GeoViews'
authors = u'HoloViz Developers'
copyright = u'2018-2019 ' + authors
description = 'Geographic visualizations for HoloViews.'

import geoviews
version = release = str(geoviews.__version__)

html_static_path += ['_static']
html_theme = 'sphinx_holoviz_theme'
html_theme_options = {
    'logo':'logo.png',
    'logo': 'logo_horizontal.png',
    'include_logo_text': False,
    'primary_color': '#35835E',
    'primary_color_dark': '#256647',
    'secondary_color': '#5f9df0',
    'second_nav': True,
}

_NAV =  (
        ('User Guide', 'user_guide/index'),
        ('Gallery', 'gallery/index'),
        ('Topics', 'topics'),
        ('About', 'about')
)

nbsite_gallery_conf = {
    'backends': ['bokeh', 'matplotlib'],
    'galleries': {
        'gallery': {'title': 'Gallery'}
    },
    'github_org': 'holoviz',
    'github_project': 'geoviews'
}

extensions += ['nbsite.gallery']

templates_path = ['_templates']

html_context.update({
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    'WEBSITE_SERVER': 'https://geoviews.org',
    'VERSION': version,
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Gitter', '//gitter.im/pyviz/pyviz'),
        ('Twitter', '//twitter.com/holoviz_org'),
        ('Github', '//github.com/holoviz/geoviews'),
    )
})
