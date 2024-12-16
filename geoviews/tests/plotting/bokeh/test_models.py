from pathlib import Path

from geoviews.models.custom_tools import _BokehCheck

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def test_bokeh_version():
    pyproject = Path(__file__).parents[4] / "pyproject.toml"
    pyproject.resolve(strict=True)
    requires = tomllib.loads(pyproject.read_text())["build-system"]["requires"]

    for req in requires:
        if req.startswith("bokeh"):
            break
    else:
        raise ValueError("Bokeh not found in build-system requires")

    assert req == _BokehCheck._bokeh_require_version
