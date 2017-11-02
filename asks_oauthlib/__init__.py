'''
Async rework of requests-oauthlib - authors of that package take all credit!
'''
import logging as _logging

from .oauth1_auth import OAuth1
from .oauth1_session import OAuth1Session
#from .oauth2_auth import OAuth2 # original still
#from .oauth2_session import OAuth2Session, TokenUpdated # original still.

__version__ = '0.1.0'

try:
    # Because asks doesn't contain a __version__ we
    # do
    import pkg_resources as _pkg_resources
    _asks_info = _pkg_resources.get_distribution('asks')
    asks_version = tuple(int(s) for s in _asks_info.version.split('.'))
    if asks_version < (1,3,6):
        _msg = ('You are using asks version %s, which is older than '
               'asks-oauthlib expects, please upgrade to 1.3.6 or later.')
        raise Warning(_msg % asks_version)
except:
    _msg = ('Unable to determine asks version, asks-oauthlib may not work with'
           'asks versions ealier than 1.3.6.')
    raise Warning(_msg)

_logging.getLogger('asks_oauthlib').addHandler(_logging.NullHandler())