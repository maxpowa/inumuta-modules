# coding=utf8
"""
ping.py - Willie Ping Module
"""
from __future__ import unicode_literals

from subprocess import Popen, PIPE
from willie.module import commands

@commands('ping')
def ping(bot, trigger):
    """
    .ping <ip/hostname> - Ping an ip or hostname
    """
    command = ['fping', '-i', '10', '-t', '500', '-p', '20', '-c', '3']
    command.append(trigger.group(3))
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
    output, error = p.communicate()
    bot.say('[Ping] '+error)
