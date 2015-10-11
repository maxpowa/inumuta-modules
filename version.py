# coding=utf8
"""
version.py - Sopel Version Module
Copyright 2009, Silas Baronda
Copyright 2014, Dimitri Molenaars <tyrope@tyrope.nl>
Licensed under the Eiffel Forum License 2.

http://sopel.dftba.net
"""
from __future__ import unicode_literals

from datetime import datetime
import sopel
import re
from os import path
import json


@sopel.module.commands('owner')
def owner(bot, trigger):
    bot.reply('I am owned by ' + bot.config.core.owner + '.')


@sopel.module.commands('version')
def version(bot, trigger):
    bot.reply('Inumuta %s' % sopel.__version__)


@sopel.module.commands('source')
def source(bot, trigger):
    bot.reply('Core: https://github.com/maxpowa/Inumuta '
              '| Modules: https://github.com/maxpowa/inumuta-modules')


@sopel.module.rule('.*')
def ctcp_version(bot, trigger):
    if ('intent' in trigger.tags and 
            trigger.tags['intent'].upper() == 'VERSION'):
        bot.notice('\x01VERSION Inumuta %s\x01' % sopel.__version__,
                   destination=trigger.nick)


@sopel.module.rule('.*')
def ctcp_source(bot, trigger):
    if ('intent' in trigger.tags and
            trigger.tags['intent'].upper() == 'SOURCE'):
        bot.notice('\x01SOURCE Core: https://github.com/maxpowa/Inumuta '
              '| Modules: https://github.com/maxpowa/inumuta-modules\x01',
                   destination=trigger.nick)


@sopel.module.rule('.*')
def ctcp_ping(bot, trigger):
    if ('intent' in trigger.tags and
            trigger.tags['intent'].upper() == 'PING'):
        bot.notice('\x01PING {}\x01'.format(trigger.group()),
                   destination=trigger.nick)


@sopel.module.rule('.*')
def ctcp_time(bot, trigger):
    if ('intent' in trigger.tags and
            trigger.tags['intent'].upper() == 'TIME'):
        dt = datetime.now()
        current_time = dt.strftime("%A, %d. %B %Y %I:%M%p")
        bot.notice('\x01TIME {0}\x01'.format(current_time),
                   destination=trigger.nick)
