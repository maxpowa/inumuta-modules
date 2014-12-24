# coding=utf8
"""
github2.py - Willie Github Module
Copyright 2014 Max Gurela
Copyright 2012, Dimitri Molenaars http://tyrope.nl/
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net/
"""

from willie import web, tools
from willie.module import commands, rule, NOLIMIT, interval
from willie.formatting import bold, color
from willie.tools import get_timezone, format_time

from util import timing

import operator
from collections import deque

import sys
if sys.version_info.major < 3:
    from urllib2 import HTTPError
else:
    from urllib.error import HTTPError
import json
import re
import datetime

issueURL = (r'https?://(?:www\.)?github.com/'
             '([A-z0-9\-]+/[A-z0-9\-]+)/'
             '(?:issues|pull)/'
             '([\d]+)')
regex = re.compile(issueURL)

def configure(config):
    """
    These values are all found by signing up your bot at
    [https://github.com/settings/applications/new](https://github.com/settings/applications/new).

    | [github]  | example | purpose |
    | --------- | ------- | ------- |
    | client_id | ao123123sf12 | Github Client ID |
    | secret | 1u3432jpqj235j2oi5oji545l34j5j | Github Client Secret |
    """

    if config.option('Configure osu! module? (You will need to register on https://github.com/settings/applications/new)', False):
        config.interactive_add('github', 'client_id', 'github client id')
        config.interactive_add('github', 'secret', 'github secret')

def fetch_api_endpoint(bot, url):
    oauth = ''
    if bot.config.github.client_id and bot.config.github.secret:
        oauth = '?client_id=%s&client_secret=%s' % (bot.config.github.client_id, bot.config.github.secret)
    return web.get(url + oauth)

@rule('.*%s.*' % issueURL)
def issue_info(bot, trigger, match=None):
    match = match or trigger
    URL = 'https://api.github.com/repos/%s/issues/%s' % (match.group(1), match.group(2))

    try:
        raw = fetch_api_endpoint(bot, URL)
    except HTTPError:
        bot.say('[Github] API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    try:
        if len(data['body'].split('\n')) > 1:
            body = data['body'].split('\n')[0] + '...'
        else:
            body = data['body'].split('\n')[0]
    except (KeyError):
        bot.say('[Github] API says this is an invalid issue. Please report this if you know it\'s a correct link!')
        return NOLIMIT
    response = [
        bold('[Github]'),
        ' [', 
        match.group(1), 
        ' #', 
        str(data['number']),
        '] ',
        data['user']['login'],
        ': ',
        data['title'],
        bold(' | '),
        body
    ]
    bot.say(''.join(response))
    #bot.say(str(data))

@timing
def get_data(bot, trigger, URL):
    try:
        raw = fetch_api_endpoint(bot, URL)
        rawLang = fetch_api_endpoint(bot, URL+'/languages')
    except HTTPError:
        bot.say('[Github] API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    langData = json.loads(rawLang).items()
    langData = sorted(langData, key=operator.itemgetter(1), reverse=True)
    
    if 'message' in data:
        return bot.say('[Github] %s' % data['message'])
        
    langColors = deque(['12','08','09','13'])
        
    max = sum([pair[1] for pair in langData])
    
    data['language'] = ''
    for (key,val) in langData:
        data['language'] = data['language'] + color(str("{0:.1f}".format(float(val) / max * 100)) + '% ' + key, langColors[0]) + ' '
        langColors.rotate()
        
    timezone = get_timezone(bot.db, bot.config, None, trigger.nick)
    if not timezone:
        timezone = 'UTC'
    data['pushed_at'] = format_time(bot.db, bot.config, timezone, trigger.nick, trigger.sender, from_utc(data['pushed_at']))
    
    return data
    
    
@commands('github', 'gh')
def github_repo(bot, trigger, match=None):
    match = match or trigger
    repo = match.group(2) or match.group(1)
    
    if repo.lower() == 'status':
        current = json.loads(web.get('https://status.github.com/api/status.json'))
        status = current['status']
        if status == 'major': status = "\x02\x034Broken\x03\x02"
        elif status == 'minor': status = "\x02\x037Shakey\x03\x02"
        elif status == 'good': status = "\x02\x033Online\x03\x02"
        return bot.say('[Github] Current Status: '+status)
    elif repo.lower() == 'rate-limit':
        return bot.say(fetch_api_endpoint(bot, 'https://api.github.com/rate_limit'))
    
    if '/' not in repo:
        repo = trigger.nick.strip() + '/' + repo
    URL = 'https://api.github.com/repos/%s' % (repo.strip())
    
    data = get_data(bot, trigger, URL)
    
    if not data:
        return
        
    response = [
        bold('[Github]'),
        ' ', 
        data['full_name'], 
        ' - ',
        data['description'],
        ' | ', 
        data['language'].strip(),
        ' | Last Push: ',
        str(data['pushed_at']),
        ' | Open Issues: ',
        str(data['open_issues']),
        ' | ',
        data['html_url']
    ]
        
    bot.write(('PRIVMSG', trigger.sender), ''.join(response))
    #bot.say(''.join(response))
    
def from_utc(utcTime,fmt="%Y-%m-%dT%H:%M:%SZ"):
    """
    Convert UTC time string to time.struct_time
    """
    return datetime.datetime.strptime(utcTime, fmt)
