# coding=utf8
"""
fuckingweather.py - Sopel module for The Fucking Weather
Copyright 2013 Michael Yanovich
Copyright 2013 Edward Powell

Licensed under the Eiffel Forum License 2.

http://sopel.dftba.net
"""
from __future__ import unicode_literals
from sopel.module import commands, rate, priority, NOLIMIT
from sopel import web
import re
import HTMLParser


@commands('fucking_weather', 'fw')
@rate(30)
@priority('low')
def fucking_weather(bot, trigger):
    text = trigger.group(2)
    if not text:
        bot.reply("INVALID FUCKING PLACE. PLEASE ENTER A FUCKING ZIP CODE, OR A FUCKING CITY-STATE PAIR.")
        return
    text = web.quote(text)
    page = web.get("http://thefuckingweather.com/April/%s" % (text))
    re_mark = re.compile('<h1 class="topRemark">(.*?)</h1>')
    results = re_mark.findall(page)
    if results:
        bot.reply(HTMLParser.HTMLParser().unescape(results[0]))
    else:
        bot.reply("I CAN'T GET THE FUCKING WEATHER.")
        return bot.NOLIMIT
