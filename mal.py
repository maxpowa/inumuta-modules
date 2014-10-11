# coding=utf8
"""
mal.py - My Anime List Module
"""

from willie.module import commands, thread
import willie.web as web
import json

def search(title):
    request = web.get('http://daraku-mal-api.net/restful-services/anime/JSON/search/'+title.replace(' ', '+'))
    show = json.loads(request)
    return show

@thread(True)
@commands('mal', 'myanimelist')
def mal(bot, trigger):
    """
    .mal [-s] <show> - Search for information about anime (-s displays synopsis)
    """ 
    synopsis = False
    query = trigger.group(2)
    if trigger.group(3).strip() == '-s':
        synopsis = True
        query = trigger.group(2).replace('-s','',1)
    result = search(query.strip())
    show = result[0]
    if not 'id' in show:
        out_list = ['[MAL] Unable to find a show matching \"', trigger.group(2).strip(), '\"']
        bot.say(''.join(out_list))
    else:
        out_list = ['[MAL] ', show['title'], ' | ', show['type'], ' | Score: ', show['score'], ' | Episodes: ', show['episodes'], ' | http://myanimelist.net/anime/', show['id']]
        bot.say(''.join(out_list))
        if synopsis:
            bot.say(''.join(['[MAL] Synopsis: ', show['synopsis']]))
