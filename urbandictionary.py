# coding=utf8
"""
urbandictionary.py - Query urbandictionary
Copyright 2014 Max Gurela
Copyright 2014, justFen
Licensed under the Eiffel Forum License 2.

http://justfen.com
"""
from __future__ import unicode_literals
import re
from sopel import web
from sopel.module import commands, example, VOICE
from sopel.formatting import color
import json
import sys
if sys.version_info.major < 3:
    from urllib2 import quote
else:
    from urllib.parse import quote


@commands('ud', 'udefine', 'urbandictionary', 'urbandict', 'udict')
@example('.ud bruh')
def ud_search(bot, trigger):
    query = trigger.group(2).strip()

    url = 'http://api.urbandictionary.com/v0/define?term=%s' % (query.encode('utf-8'))
    #bot.say(url)
    try:
        response = web.get(url)
    except UnicodeError:
        bot.say('[UrbanDictionary] ENGLISH MOTHERFUCKER, DO YOU SPEAK IT?')
        return
    else:
        data = json.loads(response)
        #bot.say(str(data))
    try:
        definition = data['list'][0]['definition'].replace('\n', ' ')
    except KeyError:
        bot.say('[UrbanDictionary] Something went wrong bruh')
    except IndexError:
        bot.say('[UrbanDictionary] No results, do you even spell bruh?')
    else:
        thumbsup = color(str(data['list'][0]['thumbs_up']) + '+', '03')
        thumbsdown = color(str(data['list'][0]['thumbs_down']) + '-', '04')
        permalink = data['list'][0]['permalink']
        length = len(thumbsup) + len(thumbsdown) + len(permalink) + 35
        ellipsies = ''
        if (len(definition) + length) > 445:
            ellipsies = '...'
        udoutput = "[UrbanDictionary] %s; %.*s%s | %s >> %s %s" % (query, 445 - length, definition, ellipsies, permalink, thumbsup, thumbsdown)
        if not "spam spam" in udoutput:
            if not trigger.sender.is_nick() and bot.privileges[trigger.sender][trigger.nick] < VOICE:
                bot.notice(udoutput, destination=trigger.nick)
            else:
                bot.say(udoutput)
        else:
            if not trigger.sender.is_nick() and bot.privileges[trigger.sender][trigger.nick] < VOICE:
                bot.notice('[UrbanDictionary] Negative ghostrider', destination=trigger.nick)
            else:
                bot.say('[UrbanDictionary] Negative ghostrider')
