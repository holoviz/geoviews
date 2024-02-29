import sys
from subprocess import check_output
from textwrap import dedent


def test_no_blocklist_imports():
    check = """\
    import sys
    import geoviews as gv

    blocklist = {"panel", "IPython", "datashader", "iris", "dask"}
    mods = blocklist & set(sys.modules)

    if mods:
        print(", ".join(mods), end="")
        """

    output = check_output([sys.executable, '-c', dedent(check)])

    assert output == b""
