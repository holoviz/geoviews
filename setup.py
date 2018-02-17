#!/usr/bin/env python

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def embed_version(basepath, ref='v0.2.2'):
    """
    Autover is purely a build time dependency in all cases (conda and
    pip) except for when you use pip's remote git support [git+url] as
    1) you need a dynamically changing version and 2) the environment
    starts off clean with zero dependencies installed.
    This function acts as a fallback to make Version available until
    PEP518 is commonly supported by pip to express build dependencies.
    """
    import io, zipfile, importlib
    try:    from urllib.request import urlopen
    except: from urllib import urlopen
    try:
        url = 'https://github.com/ioam/autover/archive/{ref}.zip'
        response = urlopen(url.format(ref=ref))
        zf = zipfile.ZipFile(io.BytesIO(response.read()))
        ref = ref[1:] if ref.startswith('v') else ref
        embed_version = zf.read('autover-{ref}/autover/version.py'.format(ref=ref))
        with open(os.path.join(basepath, 'version.py'), 'wb') as f:
            f.write(embed_version)
        return importlib.import_module("version")
    except:
        return None

def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    import json
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    try:
        from param import version
    except:
        version = embed_version(basepath)
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: param>=1.6.0 unavailable. If you are installing a package, this warning can safely be ignored. If you are creating a package or otherwise operating in a git repository, you should install param>=1.6.0.")
        return json.load(open(version_file_path, 'r'))['version_string']

setup_args = dict(
    name='geoviews',
    version=get_setup_version("geoviews"),
    python_requires = '>=2.7',
    install_requires = [
        'param >=1.5.1',
        'numpy >=1.0',
        'holoviews >=1.9.4',
        'cartopy >=0.14.2',
        'bokeh >=0.12.10',
    ],
    extras_require={
        # Notebook dependencies of IPython
        # TODO: is all this necessary? maybe notebook, ipykernel or similar?
        'notebook-dependencies':[
            'jupyter',
            'pyzmq',
            'jinja2',
            'tornado',
            'jsonschema',
            'ipython',
            'pygments',
        ]},
    description='GeoViews is a Python library that makes it easy to explore and visualize geographical, meteorological, and oceanographic datasets, such as those used in weather, climate, and remote sensing research.',    
    long_description=open('README.md').read() if os.path.isfile('README.md') else 'Consult README.md',
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD 3-Clause',
    url='http://geoviews.org',
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
)

if __name__=="__main__":
    setup(**setup_args)
