# -*- coding: utf-8 -*-
import logging

from oauthlib.common import extract_params
from oauthlib.oauth1 import Client, SIGNATURE_HMAC, SIGNATURE_TYPE_AUTH_HEADER
from oauthlib.oauth1 import SIGNATURE_TYPE_BODY
from asks import PostResponseAuth, PreResponseAuth

CONTENT_TYPE_FORM_URLENCODED = 'application/x-www-form-urlencoded'
CONTENT_TYPE_MULTI_PART = 'multipart/form-data'

# TODO: determine if this is safe in the curio/trio async?
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler(__name__+'.log',encoding='utf-8'))

class RequestWrapper():
    '''
    Class to paste over differences in requests.Request and
    asks.Request object field names.
    '''
    def __init__(self,r):
        self.r = r

    @property
    def url(self):
        return self.r.uri

    @property.setter
    def url(self,value):
        r.uri = url

    @property
    def body(self):
        return self.r.body

    @property.setter
    def body(self,value):
        r.data = value


# OBS!: Correct signing of requests are conditional on invoking OAuth1
# as the last step of preparing a request, or at least having the
# content-type set properly.
# TODO: need to confirm if PostResponseAuth is always the case
# as 3 legged authorisation for twitter user apis seems to be
# two stages manual.
class OAuth1(PreResponseAuth):
    """Signs the request using OAuth 1 (RFC5849)"""

    client_class = Client

    def __init__(self, client_key,
            client_secret=None,
            resource_owner_key=None,
            resource_owner_secret=None,
            callback_uri=None,
            signature_method=SIGNATURE_HMAC,
            signature_type=SIGNATURE_TYPE_AUTH_HEADER,
            rsa_key=None, verifier=None,
            decoding='utf-8',
            encoding='utf-8',
            client_class=None,
            force_include_body=False,
            **kwargs):

        try:
            signature_type = signature_type.upper()
        except AttributeError:
            pass

        client_class = client_class or self.client_class

        # TODO:
        # Do we really need both encoding and decoding arguments,
        # surely one will do, but which should it be? asks BasicAuth
        # and DigestAuth have encoding only, but oauthlib.oauth1
        # Client (default for client_class) has decoding kwarg.
        self.encoding = encoding

        self.force_include_body = force_include_body

        self.client = client_class(client_key, client_secret, resource_owner_key,
            resource_owner_secret, callback_uri, signature_method,
            signature_type, rsa_key, verifier, decoding=decoding, **kwargs)

    # Design decision:
    # 1. This is inline with asks auth classes but does this need
    # to be an async def if we are not doing any io yet?
    # 2. client_class can be assumed safe as asks Auth class
    # __init__ methods are not async, so client_class cannot
    # be either -- as it can't be awaited.
    # 3. Keep async for now for consistency, but plan to
    # poc removal and raise as issue with asks, as outside
    # the spirit of the trio async def/def dichotomy (what
    # about curio however?)
    async def __call__(self, r):
        """Add OAuth parameters to the request.

        Parameters may be included from the body if the content-type is
        urlencoded, if no content type is set a guess is made.
        """
        # Overwriting url is safe here as request will not modify it past
        # this point.

        log.debug('Signing request %s using client %s', r, self.client)

        # Paste over differences in requests and asks Request attribute names.
        #r = RequestWrapper(r)

        request_has_no_body = not hasattr(r,'body')

        content_type = r.headers.get('Content-Type', '')

        # TODO:
        if request_has_no_body:
            if self.client.signature_type == SIGNATURE_TYPE_BODY:
                raise ValueError('request has no body but client signature '
                                 'type is SIGNATURE_TYPE_BODY')
            if self.force_include_body:
                raise ValueError('request has not body but '
                                 'force_include_body is True')
        else:
            # okay, we can do the same as requests version.
            if (not content_type and extract_params(r.body)
                    or self.client.signature_type == SIGNATURE_TYPE_BODY):
                content_type = CONTENT_TYPE_FORM_URLENCODED
        if not isinstance(content_type, str):
            content_type = str(content_type,self.encoding)

        is_form_encoded = (CONTENT_TYPE_FORM_URLENCODED in content_type)

        log.debug('Including body in call to sign: %s',
                  is_form_encoded or self.force_include_body)

        # ASSUME this ensures r.prepare_headers call does
        # the right thing.
        if is_form_encoded:
            r.headers['Content-Type'] = CONTENT_TYPE_FORM_URLENCODED

        if request_has_no_body:
            r.url, headers, _ = self.client.sign(
                str(r.url,self.encoding), str(r.method,self.encoding), None, r.headers)
        elif self.force_include_body:
            r.url, headers, r.body = self.client.sign(
                str(r.url,self.encoding), str(r.method,self.encoding), r.body or '', r.headers)
        else:
            r.url, headers, r.body = self.client.sign(
                str(r.url,self.encoding), str(r.method,self.encoding), None, r.headers)

        r.prepare_headers(headers)
        r.url = str(r.url,self.encoding)
        print('{}'.format(r.url))
        print('{}'.format(headers))
        log.debug('Updated url: %s', r.url)
        log.debug('Updated headers: %s', headers)
        log.debug('Updated body: %r', r.body)
        return r
