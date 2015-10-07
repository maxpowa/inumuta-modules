# coding=utf8
from __future__ import unicode_literals
import urllib
import urllib2
from sopel.module import commands, rule
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/17.0' \
             ' Firefox/17.0'


@commands('prem', 'premium', 'leech')
def premium(bot, trigger):
    if not trigger.group(2):
        bot.say('You must provide a link!')
        return

    resp = get_soup(request_premium(trigger.group(2).strip()))
    bot.say('[Premium4] ' + resp.text.strip())


def request_premium(url_scrape):
    url = 'http://premium4.us/index.php'
    values = dict(urllist=url_scrape, captcha='none')
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    req.add_header('User-Agent', user_agent)
    rsp = urllib2.urlopen(req)
    content = rsp.read()
    return content


def get_soup(content):
    return BeautifulSoup(content, 'lxml')
