#!/bin/bash

SRC_DIR=$RECIPE_DIR/..
pushd $SRC_DIR

$PYTHON setup.py --quiet install --single-version-externally-managed --record=record.txt

cp -r $SRC_DIR/notebooks/ $PREFIX/share/geoviews-examples/
popd
