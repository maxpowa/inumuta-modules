# coding=utf8
"""
osu.py - A module for querying Osu! services
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.

Uses the osu!api, docs: https://github.com/peppy/osu-api/wiki
"""
from __future__ import unicode_literals
from willie.module import commands,rule
from willie.formatting import color
import willie.web as web
import json
import types

def configure(config):
    """
    These values are all found by signing up your bot at
    [https://osu.ppy.sh/p/api](https://osu.ppy.sh/p/api).

    | [osu] | example | purpose |
    | --------- | ------- | ------- |
    | api_key | b8ac80a7bdb556da303f4154bae451b1640e8e75 | osu api key |
    """

    if config.option('Configure osu! module? (You will need to register on https://osu.ppy.sh/p/api)', False):
        config.interactive_add('osu', 'api_key', 'osu api key')

apikey = ''

def setup(willie):
    if not willie.config.osu.api_key:
        raise ConfigurationError('Could not configure the osu! module. Is the API key configured properly?')

@rule('.*osu\.ppy\.sh/(u)/(\w+).*')
@commands('osu')
def osu_user(bot, trigger):
    """
    .osu [user] - Show information on an osu! user
    """
    data = '?k=%s&u=%s' % (bot.config.osu.api_key, str(trigger.group(2)))
    #bot.say(url)
    raw = web.get('https://osu.ppy.sh/api/get_user'+data)
    response = json.loads(raw)
    if not response:
        bot.say('['+color('osu!', u'13')+'] '+'Invalid user')
        return
    if not response[0]:
        bot.say('['+color('osu!', u'13')+'] '+'Invalid user')
        return
    user = response[0]
    level = 0
    accuracy = 0
    try:
        level = int(float(user['level']))
        accuracy = int(float(user['accuracy']))
    except:
        pass
    output = [
        '[', color('osu!', u'13'), '] ',
        str(user['username']),
        ' | Level ',
        str(level),
        ' | Rank ',
        str(user['pp_rank']),
        ' | Play Count ',
        str(user['playcount']),
        ' | Ranked Score ',
        str(user['ranked_score']),
        ' | Total Score ',
        str(user['total_score']),
        ' | Accuracy ~',
        str(accuracy),
        '%'
    ]
    bot.say(''.join(output))
    
@rule('.*osu\.ppy\.sh/(s|b)/(\d+).*')
def osu_beatmap(bot, trigger):
    data = '?k=%s&%s=%s' % (bot.config.osu.api_key, str(trigger.group(1)), str(trigger.group(2)))
    #bot.say(url)
    raw = web.get('https://osu.ppy.sh/api/get_beatmaps'+data)
    topscore = None
    if trigger.group(1) == 'b':
        rawscore = web.get('https://osu.ppy.sh/api/get_scores'+data)
        topscore = json.loads(rawscore)[0]
    response = json.loads(raw)
    if not response[0]:
        bot.say('['+color('osu!', u'13')+'] '+' Invalid link')
        return
    beatmap = response[0];
    m, s = divmod(int(beatmap['total_length']), 60)
    output = [
        '[', color('osu!', u'13'), '] ',
        beatmap['artist'],
        ' - ',
        beatmap['title'],
        ' (Mapped by ',
        beatmap['creator'],
        ') | ',
        str(m), 'm, ', str(s), 's',
        ' | ',
        beatmap['version'],
        ' | Difficulty: ',
        beatmap['difficultyrating'],
        ' | ',
        beatmap['bpm'],
        ' BPM'
    ]
    if topscore:
        output += (' | High Score: '+topscore['score']+' ('+topscore['rank']+') - '+topscore['username'])
    bot.say(''.join(output))
