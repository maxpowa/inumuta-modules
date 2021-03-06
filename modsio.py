# coding=utf-8
"""
modsio.py - Mods.io Sopel module
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel import web, tools
from sopel.module import rule
from sopel.formatting import color

import json
import re


def setup(sopel):
    regex = re.compile('mods\.io/mods/(\d+)')
    if not sopel.memory.contains('url_callbacks'):
        sopel.memory['url_callbacks'] = tools.SopelMemory()
    sopel.memory['url_callbacks'][regex] = get_page_info


def get_prefix():
    prefix = color('[', 'grey') + 'mods' + color('.io', 'red') + color(']', 'grey')
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
