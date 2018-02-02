#!/usr/bin/env python

import os
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup_args = {}
install_requires = ['param>=1.5.1', 'numpy>=1.0', 'holoviews>=1.9.0',
                    'cartopy>=0.14.2']
extras_require={}

# Notebook dependencies of IPython
extras_require['notebook-dependencies'] = ['jupyter', 'pyzmq', 'jinja2', 'tornado',
                                           'jsonschema',  'ipython', 'pygments']

setup_args.update(dict(
    name='geoviews',
    version="1.4.2",
    install_requires = install_requires,
    extras_require = extras_require,
    description='GeoViews.',
    long_description=open('README.md').read() if os.path.isfile('README.md') else 'Consult README.md',
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='https://github.com/ioam/geoviews',
    packages = ["geoviews",
                "geoviews.data",
                "geoviews.element",
                "geoviews.operation",
                "geoviews.plotting",
                "geoviews.plotting.bokeh",
                "geoviews.plotting.mpl"],
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 1 - Planning Development Status",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries"]
))

if __name__=="__main__":

    if 'GEOVIEWS_RELEASE' in os.environ:

        if ('upload' in sys.argv) or ('sdist' in sys.argv):
            import geoviews
            geoviews.__version__.verify(setup_args['version'])

    setup(**setup_args)
