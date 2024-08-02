#!/usr/bin/env bash

set -euxo pipefail

PACKAGE="geoviews"

python -m build . # Can add -w when this is solved: https://github.com/pypa/hatch/issues/1305

VERSION=$(python -c "import $PACKAGE; print($PACKAGE._version.__version__)")
export VERSION

BK_CHANNEL=$(python -c "
import bokeh
from packaging.version import Version

if Version(bokeh.__version__).is_prerelease:
    print('bokeh/label/dev')
else:
    print('bokeh')
")

conda build scripts/conda/recipe-core --no-anaconda-upload --no-verify -c "$BK_CHANNEL" -c pyviz/label/dev
conda build scripts/conda/recipe-recommended --no-anaconda-upload --no-verify  -c "$BK_CHANNEL" -c pyviz/label/dev

mv "$CONDA_PREFIX/conda-bld/noarch/$PACKAGE-core-$VERSION-py_0.tar.bz2" dist
mv "$CONDA_PREFIX/conda-bld/noarch/$PACKAGE-$VERSION-py_0.tar.bz2" dist
