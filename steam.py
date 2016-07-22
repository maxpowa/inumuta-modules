# coding=utf8
"""
steam.py - Show steam application prices/releases/etc

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel import module, web, tools
from bs4 import BeautifulSoup
import re

steam_re = r'(.*:)//(store.steampowered.com)(:[0-9]+)?(.*)'


def setup(bot):
    regex = re.compile(steam_re)
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = tools.SopelMemory()
    bot.memory['url_callbacks'][regex] = steam_url


def get_steam_info(url):
    # we get the soup manually because the steam pages have some odd encoding troubles
    headers = { 'Cookie':'lastagecheckage=1-January-1992; birthtime=694252801' }
    page = web.get(url, headers=headers)
    soup = BeautifulSoup(page, 'html.parser', from_encoding="utf-8")

    name = soup.find('div', {'class': 'apphub_AppName'}).text
    desc = soup.find('div', {'class': 'game_description_snippet'}).text.strip()
    desc = (desc[:127] + '...') if len(desc) > 130 else desc

    # the page has a ton of returns and tabs
    rel_date = soup.find('span', {'class': 'date'}).text.strip()
    tags = soup.find('div', {'class': 'glance_tags'}).text.strip().replace('Free to Play', '').replace('+', '').split()
    genre = "Genre: " + ', '.join(tags[:4])
    date = "Release date: " + rel_date.replace("Release Date: ", "")
    price = 'TBA'
    pricediv = soup.find('div', {'class': 'game_purchase_price price'})
    if pricediv:
        price = pricediv.text.strip()
    if not "Free to Play" in price:
        price = "Price: " + price

    return '[Steam] {}: {} | {} | {} | {}'.format(name, desc, genre, date, price)


@module.rule(steam_re)
def steam_url(bot, match):
    return bot.say(get_steam_info("http://store.steampowered.com" + match.group(4)))


@module.commands('steam')
def steamsearch(bot, trigger):
    """
    .steam [search] - Search for specified game/trailer/DLC
    """
    inp = trigger.group(2)
    if not inp:
        return bot.reply(steamsearch.__doc__.strip())
    page = web.get("http://store.steampowered.com/search/?term=" + inp)
    soup = BeautifulSoup(page, 'html.parser', from_encoding="utf-8")
    result = soup.find('a', {'class': 'search_result_row'})
    try:
        return bot.say(get_steam_info(result['href']) + " - " + result['href'].split('?')[0])
    except:
        return bot.say('[Steam] Failed to find game')
