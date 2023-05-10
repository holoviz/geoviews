import inspect
import os
import warnings

import holoviews as hv
import param

from packaging.version import Version

__all__ = (
    "deprecated",
    "find_stack_level",
    "GeoviewsDeprecationWarning",
    "GeoviewsUserWarning",
    "warn",
)


def warn(message, category=None, stacklevel=None):
    if stacklevel is None:
        stacklevel = find_stack_level()

    warnings.warn(message, category, stacklevel=stacklevel)


def find_stack_level():
    """
    Find the first place in the stack that is not inside
    Geoviews, Holoviews, or Param.

    Inspired by: pandas.util._exceptions.find_stack_level
    """
    import geoviews as gv

    pkg_dir = os.path.dirname(gv.__file__)
    test_dir = os.path.join(pkg_dir, "tests")
    param_dir = os.path.dirname(param.__file__)
    hv_dir = os.path.dirname(hv.__file__)

    frame = inspect.currentframe()
    stacklevel = 0
    while frame:
        fname = inspect.getfile(frame)
        if (
            fname.startswith(pkg_dir)
            or fname.startswith(param_dir)
            or fname.startswith(hv_dir)
        ) and not fname.startswith(test_dir):
            frame = frame.f_back
            stacklevel += 1
        else:
            break

    return stacklevel


def deprecated(remove_version, old, new=None, extra=None):
    import geoviews as gv

    current_version = Version(Version(gv.__version__).base_version)

    if isinstance(remove_version, str):
        remove_version = Version(remove_version)

    if remove_version < current_version:
        # This error is mainly for developers to remove the deprecated.
        raise ValueError(
            f"{old!r} should have been removed in {remove_version}"
            f", current version {current_version}."
        )

    message = f"{old!r} is deprecated and will be removed in version {remove_version}."

    if new:
        message = f"{message[:-1]}, use {new!r} instead."

    if extra:
        message += " " + extra.strip()

    warn(message, GeoviewsDeprecationWarning)


class GeoviewsDeprecationWarning(DeprecationWarning):
    """A Geoviews-specific ``DeprecationWarning`` subclass.
    Used to selectively filter Geoviews deprecations for unconditional display.
    """


class GeoviewsUserWarning(UserWarning):
    """A Geoviews-specific ``UserWarning`` subclass.
    Used to selectively filter Geoviews warnings for unconditional display.
    """


warnings.simplefilter("always", GeoviewsDeprecationWarning)
warnings.simplefilter("always", GeoviewsUserWarning)
