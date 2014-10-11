# coding=utf8
"""
modsio.py - Mods.io Willie module
"""

from willie import web
from willie.module import rule
from willie.formatting import color

import json

def get_prefix():
    prefix = color('[','grey')+'mods'+color('.io','red')+color(']','grey')
    return prefix

def get_info(number=None):
    if number:
        url = 'https://mods.io/mods/{}.json'.format(number)
    else:
        return None
    data = web.get(url)
    data = json.loads(data)
    return data

@rule('.*https?://mods\.io/mods/(\d+).*')
def get_page_info(bot, trigger):
    requested = get_info(trigger.group(1))
    if requested is None:
        bot.say('{} Error: Mod does not exist.'.format(get_prefix()))
    message = '{} {} - {} {} Latest: {}'.format(get_prefix(), color(requested['mod']['name'], 'red'), requested['mod']['tagline'], color('|', 'red'), requested['current_version']['name'])
    bot.say(message)
