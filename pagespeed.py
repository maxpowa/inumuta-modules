# coding=utf8
"""
pagespeed.py - Google pagespeed insights module
Copyright 2015, Maxfield Gurela
Licensed under the Eiffel Forum License 2.

 ______                                               __ 
|   __ \.---.-.-----.-----.-----.-----.-----.-----.--|  |
|    __/|  _  |  _  |  -__|__ --|  _  |  -__|  -__|  _  |
|___|   |___._|___  |_____|_____|   __|_____|_____|_____|
              |_____|           |__|                     
"""
from __future__ import unicode_literals

from willie.module import commands
from willie import web
import json
import math


def configure(config):
    """
    Google api key can be created by signing up your bot at
    [https://console.developers.google.com](https://console.developers.google.com).

    | [google]     | example                        | purpose                               |
    | ------------ | ------------------------------ | ------------------------------------- |
    | public_key   | aoijeoifjaSIOAohsofhaoAS       | Google API key (server key preferred) |
    """

    if config.option('Configure youtube module? (You will need to register a new application at https://console.developers.google.com/)', False):
        config.interactive_add('google', 'public_key', None)


@commands('pagespeed')
def show_pagespeed(bot, trigger):
    """.pagespeed <url> - Get the performance of a given website"""
    if not bot.config.has_section('google') or not bot.config.google.public_key:
        return bot.say('Pagespeed calculation cannot be performed because the module has not been configured.')
    if not trigger.group(2):
        return bot.say(show_pagespeed.__doc__)
    url = trigger.group(2)
    if not url.startswith('http'):
        url = 'http://' + url
    params = {
        'url': url,
        'key': bot.config.google.public_key,
    }
    query_string = "&".join(
        "{key}={value}".format(key=key, value=value)
        for key, value in params.items()
    )
    raw = web.get('https://www.googleapis.com/pagespeedonline/v2/runPagespeed?' + query_string)
    result = json.loads(raw)

    out = {}
    out['title'] = result['title']
    out['score'] = result['ruleGroups']['SPEED']['score']
    out['numRes'] = result['pageStats']['numberResources']
    out['numHost'] = result['pageStats']['numberHosts']
    out['reqBytes'] = round(float(result['pageStats']['totalRequestBytes']) / 1000, 2)

    out['problems'] = []
    out['fmtproblems'] = ''
    for k, v in result['formattedResults']['ruleResults'].iteritems():
        if v['ruleImpact'] > 0:
            out['problems'].append('{} (Impact: {})'.format(v['localizedRuleName'], math.ceil(v['ruleImpact'])))

    out['fmtproblems'] = ' | '.join(out['problems'])

    if len(out['problems']) > 0:
        bot.say('[PageSpeed] "{title}" | {score}/100 | Statistics: {numRes} resources downloaded, {numHost} hosts contacted resulting in {reqBytes}kB downloaded. | {fmtproblems}'.format(**out))
    else:
        bot.say('[PageSpeed] "{title}" | {score}/100 | Statistics: {numRes} resources downloaded, {numHost} hosts contacted resulting in {reqBytes}kB downloaded.'.format(**out))
