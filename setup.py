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

def embed_version(basepath, ref='v0.2.1'):
    """
    Autover is purely a build time dependency in all cases (conda and
    pip) except for when you use pip's remote git support [git+url] as
    1) you need a dynamically changing version and 2) the environment
    starts off clean with zero dependencies installed.
    This function acts as a fallback to make Version available until
    PEP518 is commonly supported by pip to express build dependencies.
    """
    import io, zipfile
    try:    from urllib.request import urlopen
    except: from urllib import urlopen
    response = urlopen('https://github.com/ioam/autover/archive/{ref}.zip'.format(ref=ref))
    zf = zipfile.ZipFile(io.BytesIO(response.read()))
    ref = ref[1:] if ref.startswith('v') else ref
    embed_version = zf.read('autover-{ref}/autover/version.py'.format(ref=ref))
    with open(os.path.join(basepath, 'version.py'), 'wb') as f:
        f.write(embed_version)


def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    import json, importlib
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    version = importlib.import_module("version")
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: autover unavailable. If you are installing a package, this warning can safely be ignored. If you are creating a package or otherwise operating in a git repository, you should refer to autover's documentation to bundle autover or add it as a dependency.")
        return json.load(open(version_file_path, 'r'))['version_string']

setup_args.update(dict(
    name='geoviews',
    version=get_setup_version("geoviews"),,
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
    package_data={'geoviews': ['.version']},
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
    setup(**setup_args)
