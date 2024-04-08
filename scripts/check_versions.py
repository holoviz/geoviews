import json
from pathlib import Path

from param import version

ROOT = Path(__file__).parents[1]


def _py_version():
    return version.Version.setup_version(
        str(ROOT), "geoviews", archive_commit="$Format:%h$"
    )


def _js_version():
    with open(ROOT / "geoviews" / "package.json") as f:
        package_json = json.load(f)
    js_version = package_json["version"]
    compatible_js_version = js_version.replace("-", "")
    for dev in ("a", "b", "rc"):
        compatible_js_version = compatible_js_version.replace(dev + ".", dev)
    return js_version, compatible_js_version


def validate_js_version():
    py_version = _py_version()
    js_version, compatible_js_version = _js_version()
    if "post" not in py_version:
        py_version = py_version.split("+")[0]
        if any(dev in py_version for dev in ("a", "b", "rc")) and "-" not in js_version:
            raise ValueError(
                f"geoviews.js dev versions ({js_version}) must "
                "must separate dev suffix with a dash, e.g. "
                "v1.0.0rc1 should be v1.0.0-rc.1."
            )
        if py_version != compatible_js_version:
            raise ValueError(
                f"geoviews.js version ({js_version}) does not match "
                f"geoviews version ({py_version}). Cannot build release."
            )
    print(f"Python version:     {py_version}")
    print(f"Javascript version: {js_version}")


if __name__ == "__main__":
    validate_js_version()
