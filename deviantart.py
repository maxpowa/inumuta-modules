# coding=utf8
"""
deviantart.py - Deviantart Willie module, Displays additional info about deviantart links
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie import tools,web
from willie.module import rule
from willie.formatting import color, bold

import json
import re


def setup(willie):
    regex = re.compile('((?:.+\.)?deviantart\.com/.*)')
    if not willie.memory.contains('url_callbacks'):
        willie.memory['url_callbacks'] = tools.WillieMemory()
    willie.memory['url_callbacks'][regex] = get_page_info


def get_prefix():
    prefix = color('[', 'grey') + 'deviant' + bold('art') + color(']', 'grey')
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
    try:
        requested = get_info('http://' + trigger.group(1))
    except:
        return
    if not requested:
        bot.say('{} Error:  does not exist.'.format(get_prefix()))
    else:
        message = '{} {} by {} ({}) [{}]'.format(get_prefix(), requested['title'], requested['author_name'], requested['type'], requested['category'])
        bot.say(message)
