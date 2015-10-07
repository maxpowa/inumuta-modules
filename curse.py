# coding=utf8
"""
curse.py - Curse Sopel module
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel import web
from sopel.module import rule
from sopel.formatting import (color, bold)

import json
import re


def setup(sopel):
    regex = re.compile('(?:minecraft\.curseforge|www\.curse|curse)\.com/(?:mc-mods|mc-mods/minecraft)/(\d+)')
    if not sopel.memory.contains('url_callbacks'):
        sopel.memory['url_callbacks'] = tools.SopelMemory()
    sopel.memory['url_callbacks'][regex] = get_page_info


def get_prefix():
    prefix = color('[', 'grey') + bold(color('Curse', 'yellow')) + color(']', 'grey')
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
    except:
        return
    if requested is None:
        bot.say('{} Error: Mod does not exist.'.format(get_prefix()))
    
    try:
        message = '{} {} - {} downloads {} Latest: {}'.format(get_prefix(), color(requested['title'], 'lime'), requested['downloads']['total'], color('|', 'yellow'), requested['download']['name'])
        bot.say(message)
    except:
        return
