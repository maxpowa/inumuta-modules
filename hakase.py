# coding=utf8
"""
hakase.py - HAKASEHAKASEHAKASEHAKASE
Copyright 2014, Max Gurela http://everythingisawesome.us

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands, rule


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


@rule('(HAKASE|hakase){3,}$')
def nano(bot, trigger):
    bot.reply('\u001D' + trigger.match.string.replace("HAKASE", "NANO").replace("hakase", "nano"))


@commands('hakase')
def nanoc(bot, trigger):
    bot.reply('\u001DNANONANONANONANONANONANO')


@rule('(NANO|nano){3,}$')
def hakase(bot, trigger):
    bot.reply('\u001D' + trigger.match.string.replace("NANO", "HAKASE").replace("nano", "hakase"))


@commands('nano')
def hakasec(bot, trigger):
    bot.reply('\u001DHAKASEHAKASEHAKASEHAKASEHAKASEHAKASE')
