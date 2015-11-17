# coding=utf-8
"""
probe.py - Don't worry, it's not your butts.
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands
import socket


def probe_ip_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False


@commands('probe')
def probe_cmd(bot, trigger):
    """
    .probe <ip> <port> - Checks if the given port is open or not
    """
    if not trigger.group(2) or not trigger.group(4):
        return bot.say('[probe] .probe <ip> <port>')

    result = probe_ip_port(trigger.group(3), trigger.group(4))
    bot.say('[probe] {}:{} is {}an open port'.format(trigger.group(3), trigger.group(4), '' if result else 'not '))
