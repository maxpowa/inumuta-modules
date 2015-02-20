# coding=utf8
"""
safebooru.py - People on IRC will love your leggings fetish!
Copyright 2014 Max Gurela
Adapted for use with Willie from https://github.com/infinitylabs/uguubot/blob/master/plugins/gelbooru.py

Licensed under the Eiffel Forum License 2 (It's GPL compatible!).
"""
from __future__ import unicode_literals
from willie.module import commands, rule
from willie import web
from bs4 import BeautifulSoup
import random
import re

safebooru_cache = []
lastsearch = ''


def refresh_cache(inp):
    global safebooru_cache
    safebooru_cache = []
    num = 0
    search = ''
    if inp == '':
        search = 'rating:safe'
    else:
        search = inp.replace(' ', '+').replace('explicit', 'rating:explicit').replace('nsfw', 'rating:explicit').replace('safe', 'rating:safe').replace('sfw', 'rating:safe')
    if not 'rating:' in search:
        search += '+rating:safe'
    search = inp.replace(' ', '+').replace('explicit', 'rating:explicit').replace('nsfw', 'rating:explicit').replace('safe', 'rating:safe').replace('sfw', 'rating:safe')
    soup = get_soup('http://safebooru.org/index.php?page=dapi&s=post&q=index&limit=10&tags={}'.format(search))
    posts = soup.find_all('post')

    while num < len(posts):
        safebooru_cache.append((posts[num].get('id'), posts[num].get('score'), posts[num].get('file_url'), posts[num].get('rating'), posts[num].get('tags')))
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
        bot.say('No results for tag \'' + trigger.group(2).strip() + '\'')
        return

    id, score, url, rating, tags = safebooru_cache.pop()

    if rating is 'e':
        rating = "\x02\x034NSFW\x03\x02"
    elif rating is 'q':
        rating = "\x02\x037Questionable\x03\x02"
    elif rating is 's':
        rating = "\x02\x033Safe\x03\x02"

    bot.say(u'\x02[Safebooru]\x02 Score: \x02{}\x02 | Rating: {} | http://safebooru.org/index.php?page=post&s=view&id={} | Tags: {}'.format(score, rating, id, tags.strip()))


@rule(r'(?:.*)(?:safebooru.org.*?id=)([-_a-zA-Z0-9]+)(?: .+)?')
def safebooru_url(bot, trigger):
    soup = get_soup('http://safebooru.org/index.php?page=dapi&s=post&q=index&id={}'.format(trigger.group(1)))
    posts = soup.find_all('post')

    id, score, url, rating, tags = (posts[0].get('id'), posts[0].get('score'), posts[0].get('file_url'), posts[0].get('rating'), posts[0].get('tags'))

    if rating is 'e':
        rating = "\x02\x034NSFW\x03\x02"
    elif rating is 'q':
        rating = "\x02\x037Questionable\x03\x02"
    elif rating is 's':
        rating = "\x02\x033Safe\x03\x02"

    bot.say(u'\x02[Safebooru]\x02 Score: \x02{}\x02 | Rating: {} | Tags: {}'.format(score, rating, tags.strip()))


def get_soup(url):
    return BeautifulSoup(web.get(url), 'lxml')
