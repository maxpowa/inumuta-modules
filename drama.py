"""
drama.py - Creates drama wherever you go!
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie import web
from willie.module import commands
import re

finder = re.compile(r'.*<h1>(.+?)<\/h1>.*')

@commands('drama')
def drama(bot, trigger):
    headers = {
         'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
    }
    raw = web.get('http://asie.pl/drama.php?2', timeout=10, headers=headers)
    #bot.say(raw)
    try:
        words = finder.search(raw).group(1).split()
        out = []
        for word in words:
            out.append(word[:1] + u'\u0081' + word[1:])
        bot.say(' '.join(out))
    except Exception:
        bot.say('418 I\'m a teapot')
