# -*- coding: utf-8 -*-

from nbsite.shared_conf import *

project = u'GeoViews'
authors = u'GeoViews developers'
copyright = u'2017 ' + authors
description = 'Geographic visualizations for HoloViews.'

import geoviews
version = release = str(geoviews.__version__)

html_static_path += ['_static']
html_theme = 'sphinx_ioam_theme'
html_theme_options = {
    'logo':'logo.png',
    'favicon':'favicon.ico'
# ...
# ? css
# ? js
}

_NAV =  (
        ('User Guide', 'user_guide/index'),
        ('About', 'about')
)

html_context = {
    'PROJECT': project,
    'DESCRIPTION': description,
    'AUTHOR': authors,
    'WEBSITE_SERVER': 'https://ioam.github.io/geoviews',
    'VERSION': version,
    'NAV': _NAV,
    'LINKS': _NAV,
    'SOCIAL': (
        ('Gitter', '//gitter.im/ioam/holoviews'),
        ('Twitter', '//twitter.com/holoviews'),
        ('Github', '//github.com/ioam/geoviews'),
    ),
    'js_includes': ['custom.js', 'require.js'],
}
