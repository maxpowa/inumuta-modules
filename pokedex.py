#coding:utf8
"""
pokedex.py - Get your Pokemon fix!
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie import web
from willie.module import commands, rule, thread, example
from bs4 import BeautifulSoup
import re
import urllib2

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/17.0' \
             ' Firefox/17.0'
             
@thread(True)
@commands('dex','pokedex',u'pok\u00e9dex')
@example('.pokedex Charmander', '8')
def pokedex(bot, trigger):
    """
    .pokedex <query> - Search for a Pokemon and much, much more. See '.pokedex manual' for more information
    """
    if not trigger.group(3):
        bot.say(u'[Pok\u00E9dex] Please consult the Pok\u00E9dex manual (.pokedex manual).')
        return
        
    if trigger.group(3).lower() == 'welcome':
        bot.say(u'<Prof. Oak> Hello there! Welcome to the world of Pok\u00E9mon! My name is Oak! People call me the Pok\u00E9mon Prof! This world is inhabited by creatures called Pok\u00E9mon! For some people, Pok\u00E9mon are pets. Other use them for fights. Myself... I study Pok\u00E9mon as a profession. {nick}! Your very own Pok\u00E9mon legend is about to unfold! A world of dreams and adventures with Pok\u00E9mon awaits! Let\'s go!'.replace('{nick}', trigger.nick))
        bot.say(u'<Prof. Oak> First things first, lets get your pok\u00E9dex set up. I\'ll need you to run a couple queries to make sure it\'s working properly.')
        return
        
    if trigger.group(3).lower() == 'manual':
        bot.action(u'opens the Pok\u00E9dex man pages (transmitted via notice)')
        bot.notice(u'The pok\u00e9dex is operated with two base commands, either .dex or .pokedex', recipient=trigger.nick)
        bot.notice(u'\u200b', recipient=trigger.nick)
        bot.notice(u'You may use the pokedex to research the following things:', recipient=trigger.nick)
        bot.notice(u' - Pok\u00e9mon         .dex Abra or .dex 63', recipient=trigger.nick)
        bot.notice(u' - Pok\u00e9mon moves   .dex move:tackle', recipient=trigger.nick)
        bot.notice(u' - Pok\u00e9mon types   .dex type:psychic', recipient=trigger.nick)
        bot.notice(u' - Items           .dex item:master ball', recipient=trigger.nick)
        bot.notice(u'For language-specific results, just prepend @<lang code>. (e.g. .dex @en:charge)')
        return
    
    ##TODO: REMOVE
    bot.say(u'[Pok\u00E9dex] There\'s a time and a place for everything. But not now. http://puu.sh/cvW4m/e510f8be5b.jpg')
    return
    ##TODO: REMOVE
    
    url = 'http://veekun.com/dex/lookup?lookup='
    if trigger.group(3).isdigit() and 'pokemon:' not in trigger.group(3):
        url = 'http://veekun.com/dex/lookup?lookup=pokemon:'
    
    url = follow_redirects(bot, url+trigger.group(2).strip())
    url = urllib2.unquote(url)
    if not url:
        bot.say(u'[Pok\u00E9dex] Invalid query, please try again.')
        return
    
    bot.say(url)
    
    soup = get_soup(url)
    if soup:
        bot.say(u'[Pok\u00E9dex] Got a response...')
        try:
            crumb = soup.find('ul', id='breadcrumbs').text.lower()
        except:
            bot.say(u'[Pok\u00E9dex] Please return to Professor Oak, you are missing an important software patch. (404)')
            return
        
        if 'moves' in crumb:
            parse_move(bot, soup)
        elif u'pok\u00E9mon' in crumb:
            parse_poke(bot, soup)
        elif 'item' in crumb:
            parse_item(bot, soup)
        elif 'type' in crumb:
            parse_type(bot, soup)
        elif 'disambiguation' in crumb:
            parse_disambig(bot, soup)
        elif 'abilities' in crumb:
            parse_abilities(bot, soup)
        else:
            bot.say(u'[Pok\u00E9dex] Please return to Professor Oak, you are missing an important software patch. '+crumb)
            return
    else:
        bot.say(u'[Pok\u00E9dex] http://puu.sh/cvW4m/e510f8be5b.jpg')
        return

def follow_redirects(bot, url):
    """
    Follow HTTP 3xx redirects, and return the actual URL. Return None if
    there's a problem.
    """
    try:
        connection = web.get_urllib_object(url, 60)
        url = connection.geturl() or url
        connection.close()
    except Exception as e:
        return None
    return url
        
def get_soup(url):
    return BeautifulSoup(web.get(url, headers={'User-Agent':user_agent}), 'lxml')
    
def parse_move(bot, soup):
    bot.say(u'[Pok\u00E9dex] There\'s a time and place for everything.')
    return

def parse_poke(bot, soup):
    pokemon = dict()
    soup = soup.find('div', id='content')
    
    part = soup.find('div', class_='dex-page-portrait')
    pokemon['name'] = part.find('p', id='dex-page-name').text
    pokemon['types'] = [type.get('alt', '') for type in part.find('p', id='dex-page-types').find_all('img')]
    
    part = soup.find('div', class_='dex-page-beside-portrait')
    pokemon['abilities'] = [ability.text for ability in part.find('dl', class_='pokemon-abilities').find_all('dt')]
    
    part = soup.find('div', class_='dex-column-container')
    pokemon['gen'] = part.find_all('div', class_='dex-column')[0].find_all('dd')[0].find('img').get('alt', '')
    pokemon['number'] = part.find_all('div', class_='dex-column')[0].find_all('dd')[1].text.replace('\n','').strip()
    pokemon['gender'] = part.find_all('div', class_='dex-column')[1].find_all('dd')[0].text.replace('\n','').strip()
    pokemon['egg_type'] = part.find_all('div', class_='dex-column')[1].find_all('dd')[1].text.replace('\n','').strip()
    pokemon['steps_hatch'] = ' '.join(part.find_all('div', class_='dex-column')[1].find_all('dd')[3].text.replace('\n','').strip().split())
    pokemon['base_exp'] = part.find_all('div', class_='dex-column')[2].find_all('dd')[0].text.replace('\n','').strip()
    
    part = soup.find('table', class_='dex-pokemon-stats')
    pokemon['base_hp'] = part.find_all('div', class_='dex-pokemon-stats-bar')[0].text
    pokemon['base_atk'] = part.find_all('div', class_='dex-pokemon-stats-bar')[1].text
    pokemon['base_def'] = part.find_all('div', class_='dex-pokemon-stats-bar')[2].text
    pokemon['base_SpAtk'] = part.find_all('div', class_='dex-pokemon-stats-bar')[3].text
    pokemon['base_SpDef'] = part.find_all('div', class_='dex-pokemon-stats-bar')[4].text
    pokemon['base_speed'] = part.find_all('div', class_='dex-pokemon-stats-bar')[5].text
    pokemon['base_total'] = part.find_all('div', class_='dex-pokemon-stats-bar')[6].text
    bot.say(u'[Pok\u00E9dex] Parsed. Formatting...')
    bot.say(unicode(pokemon))
    return

def parse_item(bot, soup):
    bot.say(u'[Pok\u00E9dex] There\'s a time and place for everything.')
    return
    
def parse_type(bot, soup):
    bot.say(u'[Pok\u00E9dex] There\'s a time and place for everything.')
    return

def parse_disambig(bot, soup):
    bot.say(u'[Pok\u00E9dex] There\'s a time and place for everything.')
    return
    
def parse_abilities(bot, soup):
    bot.say(u'[Pok\u00E9dex] There\'s a time and place for everything.')
    return
