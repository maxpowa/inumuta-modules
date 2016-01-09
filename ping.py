# coding=utf-8
"""
ping.py - Sopel Ping Module
"""
from __future__ import unicode_literals

from subprocess import Popen, PIPE
from sopel.module import commands, rule, rate, event, unblockable
from sopel.tools import Identifier
import time
import sys

if sys.version_info.major < 3:
    int = long

current_milli_time = lambda: int(round(time.time() * 1000))

@commands('ping')
def ping(bot, trigger):
    """
    .ping <ip/hostname> - Ping an ip or hostname
    """
    command = ['fping', '-i', '10', '-t', '500', '-p', '20', '-c', '3']
    command.append(trigger.group(3))
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    output, error = p.communicate()
    bot.say('[Ping] ' + error)


@commands('cping')
def cping(bot, trigger):
    """
    .cping [nick] - CTCP ping an IRC user
    """
    target = trigger.nick
    if trigger.group(2) and trigger.group(3):
        target = trigger.group(3)

    target = Identifier(target)

    if not target.is_nick():
        return bot.say('[cping] You may not target anything other than a nick')

    bot.msg(target, '\x01PING {0} {1:016d}\x01'.format(trigger.sender, current_milli_time()))


@rate(5)
@rule('(\S*) (\d{16})')
@event('NOTICE')
@unblockable
def read_ping_reply(bot, trigger):
    if 'intent' not in trigger.tags:
        return

    if trigger.tags['intent'].upper() != 'PING':
        return

    target = trigger.group(1)
    try:
        initialtime = int(trigger.group(2))
    except ValueError:
        return # Not our problem

    diff = float(current_milli_time() - initialtime) / 1000

    bot.msg(target, '[cping] Reply from {}: {:.3}s'.format(trigger.nick, diff))
