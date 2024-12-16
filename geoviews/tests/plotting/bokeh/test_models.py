from pathlib import Path

import pytest

from geoviews.models.custom_tools import _BokehCheck


def test_bokeh_version():
    # Can be removed when minimum Python version is 3.11
    tomllib = pytest.importorskip("tomllib")

    pyproject = Path(__file__).parents[4] / "pyproject.toml"
    pyproject.resolve(strict=True)
    requires = tomllib.loads(pyproject.read_text())["build-system"]["requires"]

    for req in requires:
        if req.startswith("bokeh"):
            break
    else:
        raise ValueError("Bokeh not found in build-system requires")

    assert req == _BokehCheck._bokeh_require_version
