#!/usr/bin/env bash

set -euxo pipefail

PACKAGE="geoviews"

python -m build --sdist .

VERSION=$(python -c "import $PACKAGE; print($PACKAGE._version.__version__)")
export VERSION

BK_CHANNEL=$(python -c "
import bokeh
from packaging.version import Version

if Version(bokeh.__version__).is_prerelease:
    print('bokeh/label/rc')
else:
    print('bokeh')
")

# TODO(build): Remove pyviz/label/dev after panel 1.10.0 release
conda build scripts/conda/recipe-core --no-anaconda-upload --no-verify -c pyviz/label/dev -c "$BK_CHANNEL" -c conda-forge --package-format 2
conda build scripts/conda/recipe-recommended --no-anaconda-upload --no-verify -c pyviz/label/dev -c "$BK_CHANNEL" -c conda-forge --package-format 2

mv "$CONDA_PREFIX/conda-bld/noarch/$PACKAGE-core-$VERSION-py_0.conda" dist
mv "$CONDA_PREFIX/conda-bld/noarch/$PACKAGE-$VERSION-py_0.conda" dist
