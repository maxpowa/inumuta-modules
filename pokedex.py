# coding=utf-8
"""
pokedex.py - Get your Pokemon fix!
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel import web
from sopel.module import commands, rule, thread, example
from bs4 import BeautifulSoup
import re
import sys
if sys.version_info.major < 3:
    from urllib import unquote
else:
    from urllib.parse import unquote

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/17.0' \
             ' Firefox/17.0'


@thread(True)
@commands('dex', 'pokedex', 'pok\u00e9dex')
@example('.pokedex Charmander', '[Pok\u00E9dex] #004 Charmander | Fire | Blaze | Generation 1 | \u215E male, \u215B female | Egg: Monster/Dragon')
def pokedex(bot, trigger):
    """
    .pokedex <query> - Search for a Pokemon and much, much more. See '.pokedex manual' for more information
    """
    if not trigger.group(3):
        bot.say('[Pok\u00E9dex] Please consult the Pok\u00E9dex manual (.pokedex manual).')
        return

    if trigger.group(3).lower() == 'welcome':
        bot.say('<Prof. Oak> Hello there! Welcome to the world of Pok\u00E9mon! My name is Oak! People call me the Pok\u00E9mon Prof! This world is inhabited by creatures called Pok\u00E9mon! For some people, Pok\u00E9mon are pets. Other use them for fights. Myself... I study Pok\u00E9mon as a profession. {nick}! Your very own Pok\u00E9mon legend is about to unfold! A world of dreams and adventures with Pok\u00E9mon awaits! Let\'s go!'.replace('{nick}', trigger.nick))
        bot.say('<Prof. Oak> First things first, lets get your pok\u00E9dex set up. I\'ll need you to run a couple queries to make sure it\'s working properly.')
        return

    if trigger.group(3).lower() == 'manual':
        bot.action('opens the Pok\u00E9dex man pages (transmitted via notice)')
        bot.notice('The pok\u00e9dex is operated with two base commands, either .dex or .pokedex', recipient=trigger.nick)
        bot.notice('\u0081', recipient=trigger.nick)
        bot.notice('You may use the pokedex to research the following things:', recipient=trigger.nick)
        bot.notice(' - Pok\u00e9mon         .dex Abra or .dex 63', recipient=trigger.nick)
        bot.notice(' - Pok\u00e9mon stats   .dex -s Abra or .dex -s 63', recipient=trigger.nick)
        bot.notice(' - Pok\u00e9mon moves   .dex move:tackle', recipient=trigger.nick)
        bot.notice(' - Pok\u00e9mon types   .dex type:psychic', recipient=trigger.nick)
        bot.notice(' - Items           .dex item:master ball', recipient=trigger.nick)
        bot.notice('For language-specific results, just prepend @<lang code>. (e.g. .dex @en:charge)', recipient=trigger.nick)
        return

    query = trigger.group(2).strip()
    all_stats = (trigger.group(3).lower() == '-s')
    if all_stats:
        query = query.replace(trigger.group(3), '').strip()
    ##TODO: REMOVE
    #bot.say(u'[Pok\u00E9dex] There\'s a time and a place for everything. But not now. http://puu.sh/cvW4m/e510f8be5b.jpg')
    #return
    ##TODO: REMOVE

    url = 'http://veekun.com/dex/lookup?lookup='
    if trigger.group(3).isdigit() and 'pokemon:' not in trigger.group(3):
        url = 'http://veekun.com/dex/lookup?lookup=pokemon:'

    url = follow_redirects(bot, url + query)
    url = unquote(url)
    if not url:
        bot.say('[Pok\u00E9dex] Invalid query, please try again.')
        return

    soup = get_soup(url)
    if soup:
        try:
            crumb = soup.find('ul', id='breadcrumbs').text.lower()
        except:
            bot.say('[Pok\u00E9dex] Please return to Professor Oak, you are missing an important software patch. (404)')
            return

        if 'moves' in crumb:
            parse_move(bot, soup)
        elif 'pok\u00E9mon' in crumb:
            parse_poke(bot, soup, all_stats)
        elif 'item' in crumb:
            parse_item(bot, soup)
        elif 'type' in crumb:
            parse_type(bot, soup)
        elif 'disambiguation' in crumb:
            parse_disambig(bot, soup, trigger.nick)
        elif 'abilities' in crumb:
            parse_abilities(bot, soup)
        else:
            bot.say('[Pok\u00E9dex] There is no Pok\u00E9dex function that sufficiently matches what you\'re trying.')
            return
    else:
        bot.say('[Pok\u00E9dex] http://puu.sh/cvW4m/e510f8be5b.jpg')
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
    return BeautifulSoup(web.get(url, headers={'User-Agent': user_agent}), 'lxml')


def parse_move(bot, soup):
    soup = soup.find('div', id='content')
    title = soup.find('p', id='dex-page-name').text
    types = [img['title'].split(':')[0] for img in soup.find('p', id='dex-page-types').find_all('img')]

    summary = soup.find('div', class_='dex-page-beside-portrait').find('p').text

    soup = soup.find('div', class_='dex-column-container')

    power = soup.find_all('div', class_='dex-column')[0].find_all('dd')[0].text
    accuracy = soup.find_all('div', class_='dex-column')[0].find_all('dd')[1].text
    pp = soup.find_all('div', class_='dex-column')[0].find_all('dd')[2].text
    target = soup.find_all('div', class_='dex-column')[0].find_all('dd')[3].text
    effect_chance = soup.find_all('div', class_='dex-column')[0].find_all('dd')[4].text

    output = ['[Pok\u00E9dex] ', title, ' | ', types[1], '/', types[0], ' | ', summary]
    output += ' | Dmg: '
    output += power.split(';')[0].strip()
    output += ' | Acc: '
    output += accuracy.strip()
    output += ' | PP: '
    output += pp.split(',')[0].strip()
    output += ' | Flags: '

    flags = [item.find('a').text for item in soup.find_all('div', class_='dex-column')[1].find('ul').find_all('li') if not item.has_attr('class')]
    for flag in flags:
        output += flag
        output += ', '

    bot.say(''.join(output[:-2]))


def parse_poke(bot, soup, stats=False):
    pokemon = dict()
    soup = soup.find('div', id='content')

    part = soup.find('div', class_='dex-page-portrait')
    pokemon['name'] = part.find('p', id='dex-page-name').text
    pokemon['types'] = [type.get('alt', '') for type in part.find('p', id='dex-page-types').find_all('img')]

    part = soup.find('div', class_='dex-page-beside-portrait')
    pokemon['abilities'] = [ability.text for ability in part.find('dl', class_='pokemon-abilities').find_all('dt')]

    part = soup.find('div', class_='dex-column-container')
    pokemon['gen'] = part.find_all('div', class_='dex-column')[0].find_all('dd')[0].find('img').get('alt', '')
    pokemon['number'] = part.find_all('div', class_='dex-column')[0].find_all('dd')[1].text.replace('\n', '').strip().zfill(3)
    pokemon['gender'] = part.find_all('div', class_='dex-column')[1].find_all('dd')[0].text.replace('\n', '').strip()
    pokemon['egg_types'] = [egg.text for egg in part.find_all('div', class_='dex-column')[1].find('ul', class_='inline-commas').find_all('li')]
    pokemon['steps_hatch'] = ' '.join(part.find_all('div', class_='dex-column')[1].find_all('dd')[3].text.replace('\n', '').strip().split())
    pokemon['base_exp'] = part.find_all('div', class_='dex-column')[2].find_all('dd')[0].text.replace('\n', '').strip()

    part = soup.find('table', class_='dex-pokemon-stats')
    pokemon['base_hp'] = part.find_all('div', class_='dex-pokemon-stats-bar')[0].text
    pokemon['base_atk'] = part.find_all('div', class_='dex-pokemon-stats-bar')[1].text
    pokemon['base_def'] = part.find_all('div', class_='dex-pokemon-stats-bar')[2].text
    pokemon['base_SpAtk'] = part.find_all('div', class_='dex-pokemon-stats-bar')[3].text
    pokemon['base_SpDef'] = part.find_all('div', class_='dex-pokemon-stats-bar')[4].text
    pokemon['base_speed'] = part.find_all('div', class_='dex-pokemon-stats-bar')[5].text
    pokemon['base_total'] = part.find_all('div', class_='dex-pokemon-stats-bar')[6].text

    output = []
    if not stats:
        output += '[Pok\u00E9dex] #'
        output += pokemon['number']
        output += ' '
        output += pokemon['name']
        output += ' | '
        for type in pokemon['types']:
            output += type
            output += '/'
        output.pop()
        output += ' | '
        for ability in pokemon['abilities']:
            output += ability
            output += '/'
        output.pop()
        output += ' | '
        output += pokemon['gen']
        output += ' | '
        output += pokemon['gender']
        output += ' | Egg: '
        for ability in pokemon['egg_types']:
            output += ability
            output += '/'
        output.pop()
    else:
        output += '[Pok\u00E9dex] #'
        output += pokemon['number']
        output += ' '
        output += pokemon['name']
        output += ' | '
        output += pokemon['base_exp']
        output += ' EXP | Speed '
        output += pokemon['base_speed']
        output += ' | '
        output += pokemon['base_hp']
        output += ' HP | Attack '
        output += pokemon['base_atk']
        output += ' | Defense '
        output += pokemon['base_def']
        output += ' | Sp. Atk '
        output += pokemon['base_SpAtk']
        output += ' | Sp. Def '
        output += pokemon['base_SpDef']
        output += ' | Total '
        output += pokemon['base_total']

    bot.say(''.join(output))
    return


def parse_item(bot, soup):
    soup = soup.find('div', id='content')
    title = soup.find('p', id='dex-page-name').text

    soup = soup.find('div', class_='dex-page-beside-portrait')
    summary = soup.find('p').text

    cost = soup.find('dl').find_all('dd')[0].text.strip()
    flags = [item.text for item in soup.find('dl').find('ul', class_='classic-list').find_all('li')]

    output = ['[Pok\u00E9dex] ', title, ' | ', cost, ' | ', summary, ' | Flags: ']
    for flag in flags:
        output += flag.lower()
        output += ', '
    bot.say(''.join(output[:-2]))


def parse_type(bot, soup):
    soup = soup.find('div', id='content')
    title = soup.find('p', id='dex-page-name').text

    soup = soup.find('div', class_='dex-page-beside-portrait')
    dealt = soup.find_all('ul', class_='dex-type-list')[0].find_all('li')
    taken = soup.find_all('ul', class_='dex-type-list')[1].find_all('li')

    for i, li in enumerate(dealt):
        dealt[i] = (li.find('a').find('img').get('title'), li.text.strip())
    dealt.sort(key=lambda x: x[1])

    for i, li in enumerate(taken):
        taken[i] = (li.find('a').find('img').get('title'), li.text.strip())
    taken.sort(key=lambda x: x[1])

    red = '\x034'
    green = '\x033'
    yellow = '\x038'
    reset = '\x03'

    output = ['[Pok\u00E9dex] ', title, ' | Legend:', green, ' 2x', reset, yellow, ' \xbdx', reset, red, ' 0x', reset, ' | Damage Dealt: ']
    for type, value in dealt:
        if value != '1' and type != title:
            if value == '0':
                type = red + type + reset
            elif value == '\xbd':
                type = yellow + type + reset
            elif value == '2':
                type = green + type + reset
            output += type
            output += ', '
    output = output[:-2]
    output += ' | Damage Taken: '
    for type, value in taken:
        if value != '1' and type != title:
            if value == '0':
                type = red + type + reset
            elif value == '\xbd':
                type = yellow + type + reset
            elif value == '2':
                type = green + type + reset
            output += type
            output += ', '

    bot.say(''.join(output[:-2]))


def parse_abilities(bot, soup):
    soup = soup.find('div', id='content')
    title = soup.find('p', id='dex-page-name').text
    summary = re.sub(r'\(.+\)$', '', soup.find('div', class_='dex-page-beside-portrait').find('div', class_="markdown").text)
    bot.say('[Pok\u00E9dex] ' + title + ': ' + summary)


def parse_disambig(bot, soup, sender=None):
    soup = soup.find('div', id='content')

    things = [' '.join(thing.text.replace('\n', '').split()) for thing in soup.find('ul', class_="classic-list").find_all('li')]
    things = [thing for thing in things if 'Conquest' not in thing]

    if (len(things) > 10):
        things = things[:10]
    bot.say('[Pok\u00E9dex] Sorry, I couldn\'t find exactly what you\'re looking for. I did find ' + str(len(things)) + ' possible results though. (transmitted via notice)')
    [bot.notice(' - ' + re.sub(r'\(.+\)$', '', thing), recipient=sender) for thing in things]
