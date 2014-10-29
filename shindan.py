"""
shindan.py - Be fucking annoying, all the time!
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie import web
from willie.module import commands
from bs4 import BeautifulSoup
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
    soup = get_soup(web.post('http://en.shindanmaker.com/'+trigger.group(3).strip(), data))
    shindan = soup.find(attrs={'class':re.compile("result")})
    try:
        bot.say(shindan.text.strip())
    except Exception as e:
        bot.say('418 I\'m a teapot')

def get_soup(raw):
    return BeautifulSoup(raw, 'lxml')