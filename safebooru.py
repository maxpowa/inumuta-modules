# coding=utf8
"""
safebooru.py - People on IRC will love your leggings fetish!
Copyright 2014 Max Gurela
Adapted for use with Sopel from https://github.com/infinitylabs/uguubot/blob/master/plugins/gelbooru.py

Licensed under the Eiffel Forum License 2 (It's GPL compatible!).
"""
from __future__ import unicode_literals
from sopel.module import commands, rule
from sopel import tools, web
from bs4 import BeautifulSoup
import random
import re

safebooru_cache = []
lastsearch = ''


def setup(sopel):
    regex = re.compile('safebooru.org.*(?:\?|&)id\=([-_a-zA-Z0-9]+)')
    if not sopel.memory.contains('url_callbacks'):
        sopel.memory['url_callbacks'] = tools.SopelMemory()
    sopel.memory['url_callbacks'][regex] = safebooru_url


def refresh_cache(inp):
    global safebooru_cache
    safebooru_cache = []
    num = 0
    search = []
    if inp == '':
        search = ['rating:safe']
    else:
        search = inp.split(' ')

    soup = get_soup('http://safebooru.org/index.php?page=dapi&s=post&q=index&limit=25&tags={}'.format(' '.join(search)))
    posts = soup.find_all('post')

    while num < len(posts):
        safebooru_cache.append((posts[num].get('id'), posts[num].get('score'), posts[num].get('file_url'), posts[num].get('rating').strip(), posts[num].get('tags')))
        num += 1

    random.shuffle(safebooru_cache)
    return


@commands('sb', 'safebooru')
def safebooru(bot, trigger):
    """
    .safebooru <tags> -- Gets a random image, based on given tags from safebooru.org
    """
    global lastsearch
    global safebooru_cache

    if trigger.group(2):
        search = trigger.group(2).strip().lower()
    else:
        search = ''
    if not search in lastsearch or len(safebooru_cache) < 2:
        refresh_cache(search)
    lastsearch = search

    if len(safebooru_cache) == 0:
        bot.say('No results for search \'' + trigger.group(2).strip() + '\'')
        return

    id, score, url, rating, tags = safebooru_cache.pop()

    if 'e' in rating:
        rating = '\x02\x034NSFW\x03\x02'
    elif 'q' in rating:
        rating = '\x02\x037Questionable\x03\x02'
    elif 's' in rating:
        rating = '\x02\x033Safe\x03\x02'

    bot.say('\x02[Safebooru]\x02 Score: \x02{}\x02 | Rating: {} | http://safebooru.org/index.php?page=post&s=view&id={} | Tags: {}'.format(score, rating, id, tags.strip()))


@rule(r'(?:.*)(?:safebooru.org.*?id=)([-_a-zA-Z0-9]+)(?: .+)?')
def safebooru_url(bot, trigger):
    soup = get_soup('http://safebooru.org/index.php?page=dapi&s=post&q=index&id={}'.format(trigger.group(1)))
    posts = soup.find_all('post')

    id, score, url, rating, tags = (posts[0].get('id'), posts[0].get('score'), posts[0].get('file_url'), posts[0].get('rating'), posts[0].get('tags'))

    if 'e' in rating:
        rating = "\x02\x034NSFW\x03\x02"
    elif 'q' in rating:
        rating = "\x02\x037Questionable\x03\x02"
    elif 's' in rating:
        rating = "\x02\x033Safe\x03\x02"

    bot.say('\x02[Safebooru]\x02 Score: \x02{}\x02 | Rating: {} | Tags: {}'.format(score, rating, tags.strip()))


def get_soup(url):
    return BeautifulSoup(web.get(url), 'lxml')
