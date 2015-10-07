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
    bot.say('I am owned by ' + bot.config.core.owner + '.')


@sopel.module.rule('\x01VERSION\x01')
@sopel.module.commands('version')
@sopel.module.rate(20)
def ctcp_version(bot, trigger):
    bot.write(('NOTICE', trigger.nick),
              '\x01VERSION Inumuta %s\x01' % sopel.__version__)


@sopel.module.commands('source')
@sopel.module.rule('\x01SOURCE\x01')
@sopel.module.rate(20)
def ctcp_source(bot, trigger):
    bot.notice('\x01SOURCE https://github.com/maxpowa/Inumuta/\x01',
               recipient=trigger.nick)


@sopel.module.rule('.*')
@sopel.module.rate(10)
def ctcp_ping(bot, trigger):
    if 'intent' in trigger.tags and trigger.tags['intent'] == 'PING':
        bot.notice('\x01PING {}\x01'.format(trigger.group()),
                   recipient=trigger.nick)


@sopel.module.rule('\x01TIME\x01')
@sopel.module.rate(20)
def ctcp_time(bot, trigger):
    dt = datetime.now()
    current_time = dt.strftime("%A, %d. %B %Y %I:%M%p")
    bot.write(('NOTICE', trigger.nick),
              '\x01TIME {0}\x01'.format(current_time))
