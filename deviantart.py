# coding=utf8
"""
deviantart.py - Deviantart Willie module

Displays additional info about deviantart links
"""

from willie import web
from willie.module import rule
from willie.formatting import color,bold

import json

def get_prefix():
    prefix = color('[','grey')+'deviant'+bold('art')+color(']','grey')
    return prefix

def get_info(url=None):
    if url:
        api_url = 'http://backend.deviantart.com/oembed?url={}'.format(url)
    else:
        return None
    data = web.get(api_url)
    data = json.loads(data)
    return data

@rule('.*https?://((?:.+\.)?deviantart\.com/.*).*')
def get_page_info(bot, trigger):
    requested = get_info('http://' + trigger.group(1))
    if not requested:
        bot.say('{} Error:  does not exist.'.format(get_prefix()))
    else:
        message = '{} {} by {} ({}) [{}]'.format(get_prefix(), requested['title'], requested['author_name'], requested['type'], requested['category'])
        bot.say(message)
