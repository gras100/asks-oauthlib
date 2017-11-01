'''
Async rework of requests-oauthlib - authors of that package take all credit!
'''
import logging

from .oauth1_auth import OAuth1
from .oauth1_session import OAuth1Session
from .oauth2_auth import OAuth2
from .oauth2_session import OAuth2Session, TokenUpdated

__version__ = '0.1.0'

try:
	import pkg_resources
	try:
		asks_info = pkg_resources.get_distribution('asks')
		asks_version = tuple(int(s) for s in asks_info.version.split('.'))
		if asks_version < (1,3,6):
			msg = ('You are using asks version %s, which is older than '
				   'asks-oauthlib expects, please upgrade to 1.3.6 or later.')
			raise Warning(msg % asks_version)
	except:
		raise
except:
	msg = ('Unable to determine asks version, asks-oauthlib may not work with'
		   'asks versions ealier than 1.3.6.')
    raise Warning(msg)

logging.getLogger('asks_oauthlib').addHandler(logging.NullHandler())