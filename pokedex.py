"""
pokedex.py - Get your Pokemon fix!
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

import urllib2
from willie.module import commands, rule, thread
from bs4 import BeautifulSoup
import re

@thread(True)
@commands('dex','pokedex')
def pokedex(bot, trigger):
    """
    .pokedex [name|id] - Search for a Pokemon
    """
    if not trigger.group(3):
        bot.say('[Pokedex] You must specify a Pokemon name or number.')
        return
    url = 'http://veekun.com/dex/pokemon/search?name='
    if trigger.group(3).isdigit():
        url = 'http://veekun.com/dex/pokemon/search?id='
    soup = get_soup(request(url+trigger.group(2).strip()))
    results = soup.find('div', id='content').find_all('tr')
    pokemon_results = []
    bot.say('[Pokedex] Working...')
    for result in results[1:]:
        unparse = '>'.join(result.text.split('\n'))
        if (len(unparse) < 10):
            break
        unparse = re.sub(r'(>)\1+', r'\1', unparse)
        result = filter(None, unparse.split('>'))
        #bot.say(unparse)
        if (len(result) == 10):
            pokemon_results.append({'n':result[0], 'a':result[1], 'egg':result[2], 'hp':result[3], 'atk':result[4], 'def':result[5], 'spa':result[6], 'spd':result[7], 'speed':result[8], 'tot':result[9]})
        else:
            pokemon_results.append({'n':result[0], 'a':result[1]+'/'+result[2], 'egg':result[3], 'hp':result[4], 'atk':result[5], 'def':result[6], 'spa':result[7], 'spd':result[8], 'speed':result[9], 'tot':result[10]})
    for pokemon in pokemon_results:
        bot.say('[Pokedex] {} | Abilities: {} | Egg: {} | Speed: {} | Stat Total: {} | {} HP | {} ATK | {} DEF | {} SpA | {} SpD'.format(pokemon['n'], pokemon['a'], pokemon['egg'], pokemon['speed'], pokemon['tot'], pokemon['hp'], pokemon['atk'], pokemon['def'], pokemon['spa'], pokemon['spd']))

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/17.0' \
             ' Firefox/17.0'
        
def request(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', user_agent)
    rsp = urllib2.urlopen(req)
    return rsp.read()

def get_soup(content):
    return BeautifulSoup(content, 'lxml')