# coding=utf8
"""
surrealist.py - Collection of surrealism-related commands.
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel import web
from sopel.module import commands, rule
from bs4 import BeautifulSoup


@commands('compliment')
def compliment(bot, trigger):
    """
    .compliment [nick] - Generate a surrealist compliment
    """
    soup = get_soup('http://www.madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG')
    compliment = soup.find('h2')
    if not trigger.group(2):
        bot.reply(compliment.text.strip())
    else:
        bot.say(trigger.group(2).strip() + ', ' + compliment.text.strip())


def get_soup(url):
    return BeautifulSoup(web.get(url), 'html.parser')
