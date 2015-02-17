# coding=utf8
"""
horrible.py - Yeah. The code is horrible too
Copyright 2015 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands
import re
import random
from willie import web
from bs4 import BeautifulSoup
from bs4.element import NavigableString

@commands('hs','horriblesubs','horrible')
def horrible(bot, trigger):
    """
    .horrible [show] - View the latest HorribleSubs releases for any given show
    """
    
    latest = False
    query = trigger.group(2)
    if not query:
	latest = True

    url = 'http://horriblesubs.info/lib/search.php?value={}'
    if latest:
        url = 'http://horriblesubs.info/lib/latest.php'

    soup = BeautifulSoup(web.get(url.format(query)), 'lxml')

    ep = soup.find_all('div', {'class':'episode'})
    
    if len(ep) > 0:
        for epi in ep:
            episode = ''.join([x for x in epi.contents if isinstance(x, NavigableString)])
            resblock = epi.find_all('div', {'class':'linkful resolution-block'})
            resolutions = []
            links = []
            for res in resblock:
                links.extend([link.find('a')['href'] for link in res.find_all('span', {'class': 'ind-link'}) if 'Torrent' in link.text])
                resolutions.append(res.find('a', {'href':'#'}).text)
            bot.say('Latest: {} | Resolutions: {} | Download: {} ({})'.format(episode, ', '.join(resolutions), links[-1], resolutions[-1]))
            return
