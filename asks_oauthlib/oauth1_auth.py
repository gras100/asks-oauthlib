# -*- coding: utf-8 -*-
import logging

from oauthlib.common import extract_params
from oauthlib.oauth1 import Client, SIGNATURE_HMAC, SIGNATURE_TYPE_AUTH_HEADER
from oauthlib.oauth1 import SIGNATURE_TYPE_BODY
from asks import PostResponseAuth, PreResponseAuth
from asks.request_object import Request

from .proxy import MappedAttributesProxy

CONTENT_TYPE_FORM_URLENCODED = 'application/x-www-form-urlencoded'
CONTENT_TYPE_MULTI_PART = 'multipart/form-data'

# TODO: determine if this is safe in the curio/trio async?
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler(__name__+'.log',encoding='utf-8'))


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
    # 4. __call__ in asks returns a header rather than applying
    # one, semantics confusing compared with requests unless one
    # understands that auth objects operate on headers only.
    #
    async def __call__(self, r):
        """Add OAuth parameters to the request.

        Parameters may be included from the body if the content-type is
        urlencoded, if no content type is set a guess is made.

        Discussion:
        1. refactor to work with asks request objects which in particular
        do not maintain an up to date url including e.g. queries built
        from a params object?
        2. Need to understand oauth possibilities does signing ever
        change the url for example, if so asks might be broken as the
        url is not used for io?
        """

        # Overwriting url is safe here as request will not modify it past
        # this point.

        def str_(value,encoding):
            if isinstance(value,str): return value
            return str(value,encoding)

        log.debug('Signing request %s using client %s', r, self.client)

        # Paste over differences in requests and asks Request attribute names.
        r = MappedAttributesProxy(r,url='uri',body='data')

        if r.params:
            # oauth signing is based on full uri/url including the query
            # part, unfortunately asks doesn't provide this when the query
            # is passed via params, so we have to fix up here
            r.url = '{}?{}'.format(r.url.split('?')[0],r.path.split('?')[1])

        content_type = r.headers.get('Content-Type', '')
        if (not content_type and extract_params(r.body)
                or self.client.signature_type == SIGNATURE_TYPE_BODY):
            content_type = CONTENT_TYPE_FORM_URLENCODED
        if not isinstance(content_type, str):
            content_type = str(content_type,self.encoding)

        is_form_encoded = (CONTENT_TYPE_FORM_URLENCODED in content_type)

        log.debug('Including body in call to sign: %s',
                  is_form_encoded or self.force_include_body)

        if is_form_encoded:
            r.headers['Content-Type'] = CONTENT_TYPE_FORM_URLENCODED
            r.url, headers, r.body = self.client.sign(
                str_(r.url,self.encoding), str_(r.method,self.encoding), r.body or '', r.headers)
        if self.force_include_body:
            r.url, headers, r.body = self.client.sign(
                str_(r.url,self.encoding), str_(r.method,self.encoding), r.body or '', r.headers)
        else:
            print("signing with url: {}".format(r.url))
            r.url, headers, r.body = self.client.sign(
                str_(r.url,self.encoding), str_(r.method,self.encoding), None, r.headers)

        #_r.prepare_headers(headers)
        r.url = str_(r.url,self.encoding)
        print('{}'.format(r.url))
        print('{}'.format(headers))
        log.debug('Updated url: %s', r.url)
        log.debug('Updated headers: %s', headers)
        log.debug('Updated body: %r', r.body)
        return headers
