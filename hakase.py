# coding=utf8
"""
hakase.py - HAKASEHAKASEHAKASEHAKASE
Copyright 2014, Max Gurela http://everythingisawesome.us

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import commands, rule


@commands('hakasie')
def hakasie(bot, trigger):
    """
    Nano: HAKASEHAKASEHAKASEHAKASE
    Hakase: NANONANONANONANO
    """
    if trigger.group(2):
        bot.say(trigger.group(2).strip() + ': https://www.youtube.com/embed/5MJQhe6XdWg?autoplay=1')
    else:
        bot.reply('https://www.youtube.com/embed/5MJQhe6XdWg?autoplay=1')


@rule('(HAKASE|hakase){3,}')
@commands('hakase')
def nano(bot, trigger):
    bot.reply('' + message.match.string.replace("HAKASE", "NANO").replace("hakase", "nano"))


@rule('(NANO|nano){3,}')
@commands('nano')
def hakase(bot, trigger):
    bot.reply('' + message.match.string.replace("NANO", "HAKASE").replace("nano", "hakase"))
