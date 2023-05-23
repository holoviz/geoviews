#!/usr/bin/env python

import sys,os,json
import shutil

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.sdist import sdist

import pyct.build

###############
### autover ###


def get_setup_version(reponame):
    """
    Helper to get the current version from either git describe or the
    .version file (if available).
    """
    basepath = os.path.split(__file__)[0]
    version_file_path = os.path.join(basepath, reponame, '.version')
    try:
        from param import version
    except:
        version = None
    if version is not None:
        return version.Version.setup_version(basepath, reponame, archive_commit="$Format:%h$")
    else:
        print("WARNING: param>=1.6.0 unavailable. If you are installing a package, this warning can safely be ignored. If you are creating a package or otherwise operating in a git repository, you should install param>=1.6.0.")
        return json.load(open(version_file_path, 'r'))['version_string']


#######################
### bokeh extension ###


def _build_geoviewsjs():
    from bokeh.ext import build
    print("Building custom models:")
    geoviews_dir = os.path.join(os.path.dirname(__file__), "geoviews")
    build(geoviews_dir)


class CustomDevelopCommand(develop):
    """Custom installation for development mode."""

    def run(self):
        _build_geoviewsjs()
        develop.run(self)


class CustomInstallCommand(install):
    """Custom installation for install mode."""

    def run(self):
        _build_geoviewsjs()
        install.run(self)


class CustomSdistCommand(sdist):
    """Custom installation for sdist mode."""

    def run(self):
        _build_geoviewsjs()
        sdist.run(self)


_COMMANDS = {
    'develop': CustomDevelopCommand,
    'install': CustomInstallCommand,
    'sdist':   CustomSdistCommand,
}

try:
    from wheel.bdist_wheel import bdist_wheel

    class CustomBdistWheelCommand(bdist_wheel):
        """Custom bdist_wheel command to force cancelling qiskit-terra wheel
        creation."""

        def run(self):
            """Do nothing so the command intentionally fails."""
            _build_geoviewsjs()
            bdist_wheel.run(self)

    _COMMANDS['bdist_wheel'] = CustomBdistWheelCommand
except:
    pass


####################
### dependencies ###

_required = [
    'bokeh >=3.1.0,<3.2.0',
    'cartopy >=0.18.0',
    'holoviews >=1.16.0',
    'packaging',
    'numpy',
    'shapely',
    'param',
    'panel >=1.0.0',
    'pyproj',
]

_recommended = [
    # geopandas-base installed with conda, see setup.cfg
    'geopandas',
    'netcdf4',
    'jupyter',
    'matplotlib >2.2',
    'pandas',
    'pyct',
    'scipy',
    'shapely',
    'xarray',
    'datashader',
    'pooch',
]

# can only currently run all examples with packages from conda-forge
_examples_extra = _recommended + [
    'iris >=3.5',  # Pin to support numpy 1.24
    'xesmf',
    'mock',
    'fiona',
    'geodatasets',
]

extras_require={
    'recommended': _recommended,
    'examples_extra': _examples_extra,
    'doc': _examples_extra + [
        'nbsite ==0.8.0',
        'cartopy >=0.20.0',
        'graphviz',
        'lxml',
        'selenium',
        'pooch',
    ],
    'tests': [
        'pytest-cov',
        'codecov',
        'flake8',
        'nbsmoke >=0.2.0',
        'pytest',
        'fiona',
    ],
}

extras_require['all'] = sorted(set(sum(extras_require.values(), [])))

# until pyproject.toml/equivalent is widely supported; meanwhile
# setup_requires doesn't work well with pip. Note: deliberately omitted from all.
extras_require['build'] = [
    'param >=1.9.2',
    'pyct >=0.4.4',
    'bokeh >=3.1.0,<3.2.0',
    'pyviz_comms >=0.6.0'
]

########################
### package metadata ###


setup_args = dict(
    name='geoviews',
    version=get_setup_version("geoviews"),
    python_requires = '>=3.8',
    install_requires = _required,
    extras_require = extras_require,
    tests_require = extras_require['tests'],
    description='GeoViews is a Python library that makes it easy to explore and visualize geographical, meteorological, and oceanographic datasets, such as those used in weather, climate, and remote sensing research.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD 3-Clause',
    url='https://geoviews.org',
    cmdclass=_COMMANDS,
    packages =find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'geoviews = geoviews.__main__:main'
        ]
    },
    classifiers = [
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Framework :: Matplotlib",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries"
    ]
)

if __name__=="__main__":
    example_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'geoviews','examples')

    if 'develop' not in sys.argv and 'egg_info' not in sys.argv:
        pyct.build.examples(example_path, __file__, force=True)

    setup(**setup_args)

    if os.path.isdir(example_path):
        shutil.rmtree(example_path)
