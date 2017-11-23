# -*- coding: utf-8 -*-


from nbsite.shared_conf import * # noqa

##############################################################
# start of things to edit

project = u'GeoViews'
authors = u'GeoViews developers'
copyright = u'2017 ' + authors

# TODO: rename
ioam_module = 'geoviews'
description = 'Geographic visualizations for HoloViews.'

# TODO: gah, version
version = '0.0.1'
release = '0.0.1'

html_static_path = ['_static']

html_theme = 'sphinx_ioam_theme'
html_theme_options = {
    'logo':'_static/logo.png'
    'favicon':'_static/favicon.ico'
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
    # will work without this - for canonical (so can ignore when building locally or test deploying)    
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

# end of things to edit
##############################################################

from nbsite.shared_conf2 import hack
setup, intersphinx_mapping, texinfo_documents, man_pages, latex_documents, htmlhelp_basename, html_static_path, html_title, exclude_patterns = hack(project,ioam_module,authors,description,html_static_path)
