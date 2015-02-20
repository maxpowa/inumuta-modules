# coding=utf8
"""
mal.py - My Anime List Module
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import commands, thread
import willie.web as web
import json


def search(title):
    response = '[{}]'
    if is_integer(title.strip()):
        response = web.get('https://mal-api.test.ramblingahoge.net/anime/' + web.quote(title), verify_ssl=False)
        return json.loads('[' + response + ']')
    else:
        response = web.get('https://mal-api.test.ramblingahoge.net/anime/search?q=' + web.quote(title), verify_ssl=False)
        return json.loads(response)


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@thread(True)
@commands('mal', 'myanimelist')
def mal(bot, trigger):
    """
    .mal [-s|-a] <show|id> - Search for information about an anime
    -s displays synopsis
    -a lists all search results (if more than one), result formatting: "Title (score|episode count) [id]"
    """
    synopsis = False
    list_results = False
    query = trigger.group(2)
    if trigger.group(3).strip() == '-s':
        synopsis = True
        query = trigger.group(2).replace('-s', '', 1)
    elif trigger.group(3).strip() == '-a':
        list_results = True
        query = trigger.group(2).replace('-a', '', 1)
    shows = search(query.strip())
    if len(shows) > 1 and list_results:
        out_list = ['[MAL] Found ', str(len(shows)), ' series matching your search term \'', query.strip(), '\': ']
        for show in shows:
            out_list += show['title']
            out_list += ' ('
            out_list += str(show['members_score'])
            out_list += '|'
            out_list += str(show['episodes'])
            out_list += ') ['
            out_list += str(show['id'])
            out_list += '], '
        bot.say((''.join(out_list))[:-2])
        return
    else:
        try:
            show = shows[0]
        except:
            out_list = ['[MAL] Unable to find a show matching \"', query.strip(), '\"']
            bot.say(''.join(out_list))
            return
    #bot.say(str(result))
    if not 'id' in show:
        out_list = ['[MAL] Unable to find a show matching \"', query.strip(), '\"']
        bot.say(''.join(out_list))
    else:
        out_list = ['[MAL] ', show['title'], ' | ', show['type'], ' | Score: ', str(show['members_score']), ' | Episodes: ', str(show['episodes']), ' | ', show['classification'], ' | http://myanimelist.net/anime/', str(show['id'])]
        bot.say(''.join(out_list))
        if synopsis:
            bot.say(''.join(['[MAL] Synopsis: ', show['synopsis']]))
