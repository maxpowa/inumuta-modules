# coding=utf8
"""
github2.py - Willie Github Module
Copyright 2014 Max Gurela
Copyright 2012, Dimitri Molenaars http://tyrope.nl/
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net/
"""
from __future__ import unicode_literals
from willie import web, tools
from willie.module import commands, rule, NOLIMIT, interval
from willie.formatting import bold, color
from willie.tools import get_timezone, format_time

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


def setup(willie):
    repo_url = re.compile('github\.com/([^ /]+?)/([^ /]+)/?(?!\S)')
    if not willie.memory.contains('url_callbacks'):
        willie.memory['url_callbacks'] = tools.WillieMemory()
    willie.memory['url_callbacks'][regex] = issue_info
    willie.memory['url_callbacks'][repo_url] = data_url


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

    if body.strip() == '':
        body = 'No description provided.'

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

def get_data(bot, trigger, URL):
    try:
        raw = fetch_api_endpoint(bot, URL)
        rawLang = fetch_api_endpoint(bot, URL + '/languages')
    except HTTPError:
        bot.say('[Github] API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    langData = json.loads(rawLang).items()
    langData = sorted(langData, key=operator.itemgetter(1), reverse=True)

    if 'message' in data:
        return bot.say('[Github] %s' % data['message'])

    langColors = deque(['12', '08', '09', '13'])

    max = sum([pair[1] for pair in langData])

    data['language'] = ''
    for (key, val) in langData[:3]:
        data['language'] = data['language'] + color(str("{0:.1f}".format(float(val) / max * 100)) + '% ' + key, langColors[0]) + ' '
        langColors.rotate()

    if len(langData) > 3:
        remainder = sum([pair[1] for pair in langData[3:]])
        data['language'] = data['language'] + color(str("{0:.1f}".format(float(remainder) / max * 100)) + '% Other', langColors[0]) + ' '

    timezone = get_timezone(bot.db, bot.config, None, trigger.nick)
    if not timezone:
        timezone = 'UTC'
    data['pushed_at'] = format_time(bot.db, bot.config, timezone, trigger.nick, trigger.sender, from_utc(data['pushed_at']))

    return data


@rule(r'https?://github\.com/([^ /]+?)/([^ /]+)/?(?!\S)')
def data_url(bot, trigger):
    URL = 'https://api.github.com/repos/%s/%s' % (trigger.group(1), trigger.group(2))
    fmt_response(bot, trigger, URL, True)


@commands('github', 'gh')
def github_repo(bot, trigger, match=None):
    match = match or trigger
    repo = match.group(2) or match.group(1)

    if repo.lower() == 'status':
        current = json.loads(web.get('https://status.github.com/api/status.json'))
        lastcomm = json.loads(web.get('https://status.github.com/api/last-message.json'))

        status = current['status']
        if status == 'major':
            status = "\x02\x034Broken\x03\x02"
        elif status == 'minor':
            status = "\x02\x037Shakey\x03\x02"
        elif status == 'good':
            status = "\x02\x033Online\x03\x02"

        lstatus = lastcomm['status']
        if lstatus == 'major':
            lstatus = "\x02\x034Broken\x03\x02"
        elif lstatus == 'minor':
            lstatus = "\x02\x037Shakey\x03\x02"
        elif lstatus == 'good':
            lstatus = "\x02\x033Online\x03\x02"

        timezone = get_timezone(bot.db, bot.config, None, trigger.nick)
        if not timezone:
            timezone = 'UTC'
        lastcomm['created_on'] = format_time(bot.db, bot.config, timezone, trigger.nick, trigger.sender, from_utc(lastcomm['created_on']))

        return bot.say('[Github] Current Status: ' + status + ' | Last Message: ' + lstatus + ': ' + lastcomm['body'] + ' (' + lastcomm['created_on'] + ')')
    elif repo.lower() == 'rate-limit':
        return bot.say(fetch_api_endpoint(bot, 'https://api.github.com/rate_limit'))

    if '/' not in repo:
        repo = trigger.nick.strip() + '/' + repo
    URL = 'https://api.github.com/repos/%s' % (repo.strip())

    fmt_response(bot, trigger, URL)

    #bot.say(''.join(response))

def from_utc(utcTime, fmt="%Y-%m-%dT%H:%M:%SZ"):
    """
    Convert UTC time string to time.struct_time
    """
    return datetime.datetime.strptime(utcTime, fmt)


def fmt_response(bot, trigger, URL, from_regex=False):
    data = get_data(bot, trigger, URL)

    if not data:
        return
    #bot.say(str(data))

    response = [
        bold('[Github]'),
        ' ',
        data['full_name'],
        ' - ',
        data['description']
    ]

    if not data['language'].strip() == '':
        response.extend([' | ', data['language'].strip()])

    response.extend([
        ' | Last Push: ',
        str(data['pushed_at']),
        ' | Stargazers: ',
        str(data['stargazers_count']),
        ' | Watchers: ',
        str(data['watchers_count']),
        ' | Forks: ',
        str(data['forks_count']),
        ' | Network: ',
        str(data['network_count']),
        ' | Open Issues: ',
        str(data['open_issues'])
    ])

    if not from_regex:
        response.extend([' | ', data['html_url']])

    bot.say(''.join(response))
