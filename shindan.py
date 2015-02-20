# coding=utf8
"""
shindan.py - Be fucking annoying, all the time!
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie import web
from willie.module import commands
import translate
from bs4 import BeautifulSoup
import re
import json


@commands('shindan')
def shindan(bot, trigger):
    """
    .shindan <id> [name] - Do the shindanmaker thing! Will automatically translate japanese shindans to english. (Waifu id: 215100 | Teh_Colt's Drama Gen id: 490953)
    """
    if not trigger.group(3) or not trigger.group(3).isdigit() or int(trigger.group(3).strip()) < 2000:
        bot.say(u'You must specify a shindanmaker ID (Waifu id: 215100 | T\u0081eh_Colt\'s Drama Gen id: 490953)')
        return

    name = trigger.nick
    if (trigger.group(4)):
        name = trigger.group(4)
    data = web.urlencode({'u': name, 'from': ''}).encode('ascii')
    url = follow_redirects('http://en.shindanmaker.com/' + trigger.group(3).strip())
    try:
        soup = get_soup(web.post(url, data))
        shindan = soup.find(class_='result')
        if shindan is None:
            bot.say('The shindanmaker ID %s does not exist!' % (trigger.group(3).strip(), ))
        else:
            if 'en' in url:
                bot.say(shindan.text.strip())
            else:
                msg, in_lang = translate.translate(shindan.text.strip())
                if in_lang == 'ja':
                    in_lang = 'Japanese'
                bot.say('%s (Translated from %s)' % (msg, in_lang))
    except Exception as e:
        bot.say('418 I\'m a teapot')


def follow_redirects(url):
    """
    Follow HTTP 3xx redirects, and return the actual URL. Return None if
    there's a problem.
    """
    try:
        connection = web.get_urllib_object(url, 60)
        url = connection.geturl() or url
        connection.close()
    except:
        return None
    return url


def get_soup(raw):
    return BeautifulSoup(raw, 'lxml')
