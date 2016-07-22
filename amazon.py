# coding=utf-8
"""
amazon.py - amazon plugin adapted from
https://github.com/infinitylabs/uguubot/blob/master/plugins/amazon.py

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel import tools, web
from sopel.module import commands, rule
from bs4 import BeautifulSoup
import json
import re
import sys
if sys.version_info.major >= 3:
    xrange = range


def setup(sopel):
    regex = re.compile('((www\.)?amazon\.com/[^ ]+)')
    if not sopel.memory.contains('url_callbacks'):
        sopel.memory['url_callbacks'] = tools.SopelMemory()
    sopel.memory['url_callbacks'][regex] = amazon_url


@rule(r'(https?:\/\/(www\.)?amazon\.com/[^ ]+)')
def amazon_url(bot, trigger):
    soup = get_soup(trigger.group(1))

    title = soup.find(id='productTitle')
    if not title:
        title = soup.find(id='btAsinTitle')
    if title:
        title = ' '.join(title.stripped_strings)
    else:
        title = "Unknown item"

    price = soup.find(id='priceblock_ourprice')
    if not price:
        price = soup.find("span", id='priceblock_saleprice')
    if not price:
        price = soup.find("b", class_='priceLarge')
    if price:
        price = ' '.join(price.stripped_strings)
    else:
        price = '$?'

    rating = soup.find(id='reviewStarsLinkedCustomerReviews')
    if not rating:
        rating = soup.find(id='avgRating')
    if not rating:
        rating = soup.find("div", class_='gry txtnormal acrRating')
    if rating:
        rating = ' '.join(rating.stripped_strings)


    breadcrumb = soup.find("li", class_='breadcrumb')
    if breadcrumb:
        breadcrumb = ' '.join(breadcrumb.stripped_strings)
    else:
        breadcrumb = 'Unknown'

    if rating:
        star_count = round(float(rating.split(' ')[0]), 0)
        stars = ''
        for x in xrange(0, int(star_count)):
            stars += u'\u2605'
        for y in xrange(int(star_count), 5):
            stars += u'\u2606'
    else:
        stars = '???'

    out = ['[Amazon]', title, '|', breadcrumb, '|', stars, '|', price]
    bot.say(' '.join(out))


def get_soup(url):
    return BeautifulSoup(web.get(url), 'html.parser')
