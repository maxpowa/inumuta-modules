"""
shindan.py - Be fucking annoying, all the time!
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie import web
from willie.module import commands
import re
import json

@commands('shindan')
def shindan(bot, trigger):
    """
    .shindan <id> [name] - Do the shindanmaker thing! (Waifu id: 215100 | Teh_Colt's Drama Gen id: 490953)
    """
    name = trigger.nick
    if (trigger.group(4)):
        name = trigger.group(4)
    data = web.urlencode({'u': name, 'from': ''}).encode('ascii')
    raw = web.post('http://en.shindanmaker.com/'+trigger.group(3).strip(), data)
    try:
        result = re.search('caption: "(.+)",$', raw[12500:13750].decode('ascii', 'ignore'), re.M).group(1)
        bot.say(str(result))
    except Exception as e:
        bot.say('418 I\'m a teapot')
        bot.say(str(e))