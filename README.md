[![Travis](https://api.travis-ci.org/CubeBrowser/cube-explorer.svg?branch=master)](https://travis-ci.org/CubeBrowser/cube-explorer)
[![Coveralls](https://img.shields.io/coveralls/CubeBrowser/cube-explorer.svg)](https://coveralls.io/github/CubeBrowser/cube-explorer)
[![Waffle](https://badge.waffle.io/CubeBrowser/cube-explorer.png?label=ready&title=ready)](https://waffle.io/CubeBrowser/cube-explorer)
# cube-explorer

Exploration and visualization of https://github.com/SciTools/iris cubes in a web browser, including a Jupyter notebook.

To install, first install HoloViews and Iris:

```
conda install -c ioam holoviews
conda install -c scitools iris
```

Then run setup on a copy of this git repository:

```
git clone https://github.com/CubeBrowser/cube-explorer.git
cd cube-explorer
python setup.py develop
```

You will probably also want a copy of the Iris sample data.  Sample
bash commands for downloading and linking to it:

```
cd ~
git clone https://github.com/SciTools/iris-sample-data.git
DIR=`python -c 'import iris ; print(iris.sample_data_path())'`
cd `dirname $DIR`
ln -s ~/iris-sample-data/sample_data .
```

You should now be able to run the examples in the `notebooks` directory:

```
cd ~/cube-explorer
cd notebooks
jupyter notebook
```
