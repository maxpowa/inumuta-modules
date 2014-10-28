"""
yandere.py - People on IRC will love your leggings fetish!
Copyright 2014 Max Gurela
Adapted for use with Willie from https://github.com/infinitylabs/uguubot/blob/master/plugins/yandere.py

Licensed under the Eiffel Forum License 2 (It's GPL compatible!).
"""
from willie.module import commands, rule
from bs4 import BeautifulSoup
import urllib2
import re
import random
import booruhelper

yandere_cache = []

def refresh_cache():
    "gets a page of random yande.re posts and puts them into a dictionary "
    url = 'https://yande.re/post?tags=rating:safe&page=%s' % random.randint(1,11000)
    soup = get_soup(url)

    for result in soup.findAll('li'):
        title = result.find('img', {'class': re.compile(r'\bpreview\b')}) #['title']
        img = result.find('a', {'class': re.compile(r'\bdirectlink\b')}) #['href']
        if img and title:
            title = title['title'].replace('Rating: ', '', 1)
            rating = title.split(' Score: ')
            score = rating[1].split(' Tags: ')
            tags = score[1].split(' User: ')
            user = tags[1]
            yandere_cache.append((result['id'].replace('p',''), rating[0], score[0], tags[0], user, img['href']))

def get_yandere_tags(inp):
    search = ''
    if not inp:
        search = 'rating:safe'
    else:
        search = inp.replace(' ','+').replace('explicit','rating:explicit').replace('nsfw','rating:explicit').replace('safe','rating:safe').replace('sfw','rating:safe')
    if not 'rating:' in search:
        search += '+rating:safe'
    url = 'https://yande.re/post?tags=%s' % inp.replace(' ','+')
    soup = get_soup(url)
    imagelist = soup.find('ul', {'id': 'post-list-posts'}).findAll('li')
    image = imagelist[random.randint(0,len(imagelist)-1)]
    imageid = image["id"].replace('p','')
    title = image.find('img')['title']
    rating = title.replace('Rating: ', '', 1).split(' Score: ')
    score = rating[1].split(' Tags: ')
    tags = score[1].split(' User: ')
    user = tags[1]
    src = image.find('a', {'class': 'directlink'})["href"]
    
    rating = rating[0].strip()
    if rating == 'Explicit': rating = "\x02\x034NSFW\x03\x02"
    elif rating == 'Questionable': rating = "\x02\x037Questionable\x03\x02"
    elif rating == 'Safe': rating = "\x02\x033Safe\x03\x02"

    return (u'\x02[Yande.re]\x02 Score: \x02{}\x02 | Rating: {} | https://yande.re/post/show/{} | Tags: {}'.format(score[0], rating, imageid, tags[0].strip()))

@commands('yandere', 'yande.re')
def yandere(bot, trigger):
    """
    .yandere [tags] -- Yande.re -- Gets a random image from yande.re (May return NSFW images)
    """

    if trigger.group(2): 
        bot.say(get_yandere_tags(trigger.group(2)))
        return

    id, rating, score, tags, user, image = yandere_cache.pop()
    
    if rating == 'Explicit': rating = "\x02\x034NSFW\x03\x02"
    elif rating == 'Questionable': rating = "\x02\x037Questionable\x03\x02"
    elif rating == 'Safe': rating = "\x02\x033Safe\x03\x02"
    
    bot.say(u'\x02[Yande.re]\x02 Score: \x02{}\x02 | Rating: {} | https://yande.re/post/show/{} | Tags: {}'.format(score, rating, id, tags))
    if len(yandere_cache) < 3:
        refresh_cache()

def get_soup(url):
    return BeautifulSoup(booruhelper.get(url), 'lxml')

def unquote(s):
    return urllib2.unquote(s)
    
#do an initial refresh of the cache
refresh_cache()