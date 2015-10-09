# coding=utf8
"""
jpv.py - J-Pop and Vocaloid songs
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands, rule
from sopel import web, tools
import sys
import json
import re
if sys.version_info.major < 3:
    from urllib import unquote
else:
    from urllib.parse import unquote


def setup(sopel):
    regex = re.compile('jpv\.everythingisawesome\.us/song/\?genre=(.+)&song=(.+)')
    if not sopel.memory.contains('url_callbacks'):
        sopel.memory['url_callbacks'] = tools.SopelMemory()
    sopel.memory['url_callbacks'][regex] = jpv_info


@rule('https?://jpv\.everythingisawesome\.us/song/\?genre=(.+)&song=(.+)')
def jpv_info(bot, trigger):
    song = None
    try:
        song = info(trigger.group(1).strip(), trigger.group(2).strip())
    except Exception:
        return
    bot.say('[JPV] ' + song['artist'] + ' - ' + song['title'] + ' | ' + song['album'] + ' | ' + song['album_artist'] + ' | ' + song['genre'])


def info(genre, title):
    if '.mp3' not in title:
        title = title + '.mp3'
    genre = unquote(genre)
    title = unquote(title)
    request = web.get('http://jpv.everythingisawesome.us/api/v1/song/' + genre + '/' + title)
    return json.loads(request)


def search(bot, trigger, title):
    request = web.get('http://jpv.everythingisawesome.us/api/v1/search/' + title)
    songs = json.loads(request)
    if len(songs) > 0:
        if len(songs) > 5:
            bot.say('[JPV] Search results limited to 3 results, see http://jpv.everythingisawesome.us/api/v1/search/' + title + ' for a full list')
            songs = songs[:3]
        for song in songs:
            bot.say('[JPV] ' + song['artist'] + ' - ' + song['title'] + ' | ' + song['album'] + ' | ' + song['album_artist'] + ' | ' + song['genre'] + ' | http://jpv.everythingisawesome.us/song/?song={}'.format(song['href'].replace('.mp3', '')))
    else:
        bot.say('[JPV] Unable to find a song matching \"' + trigger.group(2).strip() + '\"')


@commands('jpv')
def jpv(bot, trigger):
    search(bot, trigger, trigger.group(2).strip())
