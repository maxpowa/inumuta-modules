# coding=utf8
"""
jpv.py - J-Pop and Vocaloid songs
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands,rule
import willie.web as web
import urllib
import json

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
        title = title+'.mp3'
    genre = urllib.unquote(genre)
    title = urllib.unquote(title)
    request = web.get('http://test.everythingisawesome.us/api/v1/song/'+genre+'/'+title)
    return json.loads(request)

def search(bot, trigger, title):
    request = web.get('http://test.everythingisawesome.us/api/v1/list.php?genre=all&format=json')
    songs = json.loads(request)
    found_songs = 0
    for song in songs:
        if song:
            if song['title'].lower() == title.lower():
                found_songs = found_songs + 1
                bot.say('[JPV] ' + song['artist'] + ' - ' + song['title'] + ' | ' + song['album'] + ' | ' + song['album_artist'] + ' | ' + song['genre'] + ' | http://jpv.everythingisawesome.us/song/?song={}'.format(song['href'].replace('.mp3', '')))
    if found_songs == 0:
        bot.say('[JPV] Unable to find a song matching \"'+trigger.group(2).strip()+'\"')

@commands('jpv')
def jpv(bot, trigger): 
    search(bot, trigger, trigger.group(2).strip())
        

