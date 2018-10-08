from __future__ import absolute_import

import param
from holoviews.core.data import Dataset

try:
    from . import geopandas # noqa (API import)
except ImportError:
    pass
except Exception as e:
    param.main.warning('GeoPandas interface failed to import with '
                       'following error: %s' % e)

try:
    from . import iris # noqa (API import)
    Dataset.datatype.append('cube')
except ImportError:
    pass
except Exception as e:
    param.main.warning('Iris interface failed to import with '
                       'following error: %s' % e)

