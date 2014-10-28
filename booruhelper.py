"""
booruhelper.py - Required for the booru modules to work correctly
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2 (It's GPL compatible!).
"""
import json
import urllib
import urllib2
import urlparse
import re

from urllib import quote

ua_firefox = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/17.0' \
             ' Firefox/17.0'

def get(*args, **kwargs):
    return open(*args, **kwargs).read()

def open(url, query_params=None, user_agent=None, post_data=None,
         referer=None, get_method=None, **kwargs):

    if query_params is None:
        query_params = {}

    if user_agent is None:
        user_agent = ua_firefox

    query_params.update(kwargs)

    url = prepare_url(url, query_params)

    request = urllib2.Request(url, post_data)

    if get_method is not None:
        request.get_method = lambda: get_method

    request.add_header('User-Agent', user_agent)

    if referer is not None:
        request.add_header('Referer', referer)

    return urllib2.build_opener().open(request)


def prepare_url(url, queries):
    if queries:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)

        query = dict(urlparse.parse_qsl(query))
        query.update(queries)
        query = urllib.urlencode(dict((to_utf8(key), to_utf8(value))
                                  for key, value in query.iteritems()))

        url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))

    return url

def to_utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf8', 'ignore')
    else:
        return str(s)