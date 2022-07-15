import cartopy.crs as ccrs
import pytest

from geoviews.util import project_extents



def test_outside_extents():
    # extents outside bounds of map 32635, see https://epsg.io/32635
    extents = (-2036817.4174174175, 577054.6546546547, -1801982.5825825825, 867745.3453453453)
    dest_proj = ccrs.Mercator()
    src_proj = ccrs.epsg(32635)

    msg = (
        "Could not project data from .+? projection to .+? projection\. "
        "Ensure the coordinate reference system \(crs\) matches your data and the kdims\."
    )
    with pytest.raises(ValueError, match=msg):
        project_extents(extents, src_proj, dest_proj)
