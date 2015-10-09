# coding=utf8
"""
flex.py - FLEX YOUR DAMN DONGERS
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands


@commands('flex')
def flex(bot, trigger):
    """
    .flex [donger] - Flex 'em
    """
    if trigger.group(2):
        bot.say('\u1559\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\u1557 FLEX YOUR {} \u1559\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\u1557'.format(trigger.group(2).strip().upper()))
    else:
        bot.say('\u1559\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\u1557 flex your dongers \u1559\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\u1557')
