# coding=utf8
"""
hummingbird.py - You have no life.
Copyright 2015 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands, rule, example
from sopel.formatting import color
from sopel import web
from datetime import datetime, timedelta
import json


@commands('hbuser', 'hummingbirduser', 'hbu')
@example('.hummingbirduser maxpowa')
def hummingbirduser(bot, trigger):
    """
    .hummingbirduser [user] - Show information on a Hummingbird user
    """
    data = trigger.group(2)

    if not data:
        data = trigger.nick

    format_user(bot, data)


def format_user(bot, user):
    url = 'http://hummingbird.me/api/v1/users/{}'.format(user)
    raw = web.get(url)
    try:
        data = json.loads(raw)
    except:
        return bot.say(u'[Hummingbird] User does not exist.')

    if 'error' in data:
        return bot.say(u'[Hummingbird] An error occurred (' + data['error'] + ')')

    output = u'[Hummingbird] {name} | {website} | {about} | {life_wasted}'

    data['about'] = data['about'].strip()
    h, m = divmod(int(data['life_spent_on_anime']), 60)
    d, h = divmod(h, 24)
    data['life_wasted'] = '{} days, {} hours, {} minutes spent watching anime'.format(d, h, m)

    bot.say(output.format(**data))


@commands('hb', 'hummingbird')
@example('.hummingbird Nichijou')
def hummingbird(bot, trigger):
    """
    .Hummingbird [anime] - Show information on an anime
    """
    anime = trigger.group(2)
    if not anime:
        bot.say(u'[Hummingbird] You need to specify an anime')
    else:
        find_anime(bot, anime)


def find_anime(bot, anime):
    url = 'http://hummingbird.me/api/v1/search/anime?query='
    raw = web.get(url + anime)
    try:
        data = json.loads(raw)
    except:
        return bot.say(u'[Hummingbird] No anime found matching \'' + anime + '\'')
    if len(data) < 1:
        return bot.say(u'[Hummingbird] No anime found matching \'' + anime + '\'')
    else:
        data = data[0]

    if 'error' in data:
        return bot.say(u'[Hummingbird] An error occurred (' + data['error'] + ')')

    output = u'[Hummingbird] {title} | {show_type} | Rating: {rating} | Episodes: {episode_count} | {age_rating} | {url}'
    if data['community_rating'] != 0:
        data['rating'] = str(int(round(data['community_rating']*20))) + '%' 
    else:
        data['rating'] = '-'

    bot.say(output.format(**data))

