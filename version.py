# coding=utf8
"""
version.py - Willie Version Module
Copyright 2009, Silas Baronda
Copyright 2014, Dimitri Molenaars <tyrope@tyrope.nl>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

from datetime import datetime
import willie
import re
from os import path
import json

@willie.module.commands('owner')
def owner(bot, trigger):
    bot.say('I am owned by '+bot.config.core.owner+'.')

@willie.module.rule('\x01VERSION\x01')
@willie.module.commands('version')
@willie.module.rate(20)
def ctcp_version(bot, trigger):
    bot.write(('NOTICE', trigger.nick),
              '\x01VERSION Inumuta %s\x01' % willie.__version__)


@willie.module.commands('source')
@willie.module.rule('\x01SOURCE\x01')
@willie.module.rate(20)
def ctcp_source(bot, trigger):
    bot.write(('NOTICE', trigger.nick),
              '\x01SOURCE https://github.com/maxpowa/Inumuta/\x01')


@willie.module.rule('\x01PING\s(.*)\x01')
@willie.module.rate(10)
def ctcp_ping(bot, trigger):
    text = trigger.group()
    text = text.replace("PING ", "")
    text = text.replace("\x01", "")
    bot.write(('NOTICE', trigger.nick),
              '\x01PING {0}\x01'.format(text))


@willie.module.rule('\x01TIME\x01')
@willie.module.rate(20)
def ctcp_time(bot, trigger):
    dt = datetime.now()
    current_time = dt.strftime("%A, %d. %B %Y %I:%M%p")
    bot.write(('NOTICE', trigger.nick),
              '\x01TIME {0}\x01'.format(current_time))
