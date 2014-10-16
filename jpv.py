# coding=utf8
"""
jpv.py - J-Pop and Vocaloid songs
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands,rule
import willie.web as web
import json

@rule('https?://jpv.everythingisawesome.us/song/(.+)')
def jpv_info(bot, trigger):
    song = None
    try:
        song = info(trigger.group(1).strip())
    except Exception:
        return
    bot.say('[JPV] ' + song['artist'] + ' - ' + song['title'] + ' | ' + song['album'] + ' | ' + song['albumartist'] + ' | ' + song['genre'])

def info(title):
    request = web.get('http://jpv.everythingisawesome.us/api/song/'+title.replace(' ', '%20'))
    return json.loads(request)

def search(title):
    request = web.get('http://jpv.everythingisawesome.us/api/search/'+title.replace(' ', '+'))
    return json.loads(request)

@commands('jpv')
def jpv(bot, trigger): 
    show = search(trigger.group(2).strip())
    if show['count'] < 1:
        bot.say('[JPV] Unable to find a song matching \"'+trigger.group(2).strip()+'\"')
    else:
        if show['count'] == 1:
            bot.say('[JPV] {}'.format(show['songs'][0]))

