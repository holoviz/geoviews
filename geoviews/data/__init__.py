from __future__ import absolute_import

import param

try:
    from . import geopandas
except ImportError:
    pass
except Exception as e:
    param.main.warning('GeoPandas interface failed to import with '
                       'following error: %s' % e)

