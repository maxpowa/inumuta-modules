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
from willie.formatting import bold
import sys
if sys.version_info.major < 3:
    from urllib2 import HTTPError
else:
    from urllib.error import HTTPError
import json
import re

issueURL = (r'https?://(?:www\.)?github.com/'
             '([A-z0-9\-]+/[A-z0-9\-]+)/'
             '(?:issues|pull)/'
             '([\d]+)')
regex = re.compile(issueURL)

@rule('.*%s.*' % issueURL)
def issue_info(bot, trigger, match=None):
    match = match or trigger
    URL = 'https://api.github.com/repos/%s/issues/%s' % (match.group(1), match.group(2))

    try:
        raw = web.get(URL)
    except HTTPError:
        bot.say('The GitHub API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    try:
        if len(data['body'].split('\n')) > 1:
            body = data['body'].split('\n')[0] + '...'
        else:
            body = data['body'].split('\n')[0]
    except (KeyError):
        bot.say('The API says this is an invalid issue. Please report this if you know it\'s a correct link!')
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

@commands('github')
def cmd_github(bot, trigger):
    if trigger.group(2):
        if trigger.group(2).lower() == 'status':
            current = json.loads(web.get('https://status.github.com/api/status.json'))
            status = current['status']
            if status == 'major': status = "\x02\x034Broken\x03\x02"
            elif status == 'minor': status = "\x02\x037Shakey\x03\x02"
            elif status == 'good': status = "\x02\x033Online\x03\x02"
            bot.say('[Github] Current Status: '+status)
            
