# coding=utf8
"""
hummingbird.py - You have no life.
Copyright 2015 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import commands, rule, example
from willie.formatting import color
from willie import web
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
    url = 'https://hummingbird.me/api/v1/users/{}'.format(user)
    raw = web.get(url)
    try:
        data = json.loads(raw)
    except:
        return bot.say('[Hummingbirduser] User does not exist.')

    if 'error' in data:
        return bot.say('[Hummingbirduser] ' + data['error'])

    output = '[Hummingbirduser] {name} | {website} | {about} | {life_wasted}'

    data['about'] = data['about'].strip()
    h, m = divmod(int(data['life_spent_on_anime']), 60)
    d, h = divmod(h, 24)
    data['life_wasted'] = '{} days, {} hours, {} minutes spent watching anime'.format(d, h, m)

    bot.say(output.format(**data))

@commands('hb', 'hummingbird')
@example('.hummingbird Nichijou')
def hummingbird(bot, trigger):
    """
    .Hummingbird [Anime] - Show information on an anime
    """
    anime = trigger.group(1)
    if not data:
        bot.say("You need to specify an anime")
    else:
        find_anime(bot, anime)

def find_anime(bot, anime):
    url = 'https://hummingbird.me/api/v1/search/anime?query='
    raw = web.get(url + anime)
    try:
        data = json.lods(raw)
    except:
        return bot.say('[Hummingbird]Anime not found')

    if 'error' in data:
        return bot.say('[Hummingbird]' + data['error'])

    output = '[Hummingbird] {title} | {show_type} | Rating%: {rating}% | Episodes: {episode_count} | {age_rating} | {url}'
    if data['community_rating'] != 0:
        data['rating'] = data['community_rating']*20
    else:
        data['rating'] = '-'

    bot.say(output.format(**data))

