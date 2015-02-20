# coding=utf8
"""
hummingbird.py - You have no life.
Copyright 2015 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands,rule,example
from willie.formatting import color
from willie import web
from datetime import datetime, timedelta
import json


@commands('hb','hummingbird')
@example('.hummingbird maxpowa')
def hummingbird(bot, trigger):
    """
    .hummingbird [user] - Show information on a Hummingbird user
    """
    data = trigger.group(2)

    if not data:
        data = trigger.nick
    
    format_user(bot, data)


def format_user(bot, user):
    url = 'https://hummingbird.me/api/v1/users/{}'.format(user)
    raw = web.get(url)
    try:
        data = json.loads(raw)
    except:
        return bot.say('[Hummingbird] User does not exist.')
    
    if 'error' in data:
        return bot.say(u'[Hummingbird] '+data['error'])

    output = '[Hummingbird] {name} | {website} | {about} | {life_wasted}'

    data['about'] = data['about'].strip()
    h, m = divmod(int(data['life_spent_on_anime']), 60)
    d, h = divmod(h, 24) 
    data['life_wasted'] = '{} days, {} hours, {} minutes spent watching anime'.format(d,h,m)

    bot.say(output.format(**data))
