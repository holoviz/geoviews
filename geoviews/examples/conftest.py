# For use with pyct (https://github.com/pyviz/pyct), but just standard
# pytest config (works with pytest alone).

import os
import pytest

# ipynb in examples are "example_notebook"
def pytest_collection_modifyitems(items):
    for item in items:
        path = str(item.fspath)
        if os.path.splitext(path)[1].lower() == ".ipynb":
            item.add_marker(pytest.mark.example_notebook)
