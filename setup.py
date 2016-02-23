#!/usr/bin/env python

import sys, os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup_args = {}
install_requires = ['param>=1.3.2', 'numpy>=1.0', 'iris>=1.9.2', 'holoviews>=1.4.3']
extras_require={}

# Notebook dependencies of IPython
extras_require['notebook-dependencies'] = ['jupyter', 'pyzmq', 'jinja2', 'tornado',
                                           'jsonschema',  'ipython', 'pygments']

setup_args.update(dict(
    name='holocube',
    version="0.0.1",
    install_requires = install_requires,
    extras_require = extras_require,
    description='HoloCube.',
    long_description=open('README.md').read() if os.path.isfile('README.md') else 'Consult README.md',
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='BSD',
    url='https://github.com/CubeBrowser/cube-explorer',
    packages = ["holocube",
                "holocube.element",
                "holocube.plotting"],
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
