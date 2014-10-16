# coding=utf8
"""
github2.py - Willie Github Module
Copyright 2014 Max Gurela
Copyright 2012, Dimitri Molenaars http://tyrope.nl/
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net/
"""

from willie import web, tools
from willie.module import commands, rule, NOLIMIT
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
