# coding=utf8
"""
nyanpasu.py - nyanpasu~~
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands


@commands('nyanpasu', 'nyanpass')
def drama(bot, trigger):
    bot.say('Nyanpasu~~ http://nyanpass.com/nyanpass.mp3')
