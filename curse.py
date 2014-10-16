# coding=utf8
"""
curse.py - Curse Willie module
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie import web
from willie.module import rule
from willie.formatting import (color,bold)

import json

def get_prefix():
    prefix = color('[','grey')+bold(color('Curse','yellow'))+color(']','grey')
    return prefix

def get_info(number=None):
    if number:
        url = 'http://widget.mcf.li/{}.json'.format(number)
    else:
        return None
    data = web.get(url)
    data = json.loads(data)
    return data

@rule('.*https?://(?:minecraft\.curseforge|www\.curse|curse)\.com/(?:mc-mods|mc-mods/minecraft)/(\d+).*')
def get_page_info(bot, trigger):
    requested = None
    try:
        requested = get_info(trigger.group(1))
    except Exception:
        try:
            requested = get_info(trigger.group(1))
        except Exception:
            bot.say(get_prefix() + ' Unable to retrieve info about ' + trigger.group(1))
            return
    if requested is None:
        bot.say('{} Error: Mod does not exist.'.format(get_prefix()))
    message = '{} {} - {} downloads {} Latest: {}'.format(get_prefix(), color(requested['title'], 'lime'), requested['downloads']['total'], color('|', 'yellow'), requested['download']['name'])
    bot.say(message)
