# coding=utf-8
"""
dockerstatus.py - Check docker services status
Copyright 2016 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands
from sopel import web
from sopel.formatting import color, bold
import json


@commands('dockerstatus', 'dockers', 'ds')
def dockerstatus(bot, trigger):
    """
    .dockers - Check the status of Docker's services
    """
    try:
        raw = web.get('https://api.status.io/1.0/status/533c6539221ae15e3f000031')

        response = json.loads(raw)
        response = response.get('result', {})

        out = []
        for server in response.get('status', []):
            out.append('{} {}'.format(server['name'], format_status(server['status_code'])))
        bot.say('Overall Status: {} | {}'.format(response.get('status_overall', {}).get('status', 'Unknown'), ' '.join(out)))
    except Exception as e:
        bot.say('Docker services status check is currently offline. ({})'.format(e))


def format_status(status):
    if status == 100: 
        return color('\u2713', 'green')
    elif status >= 300 and status <= 400:
        return color('~', 'yellow')
    elif status > 400:
        return color('\u2718', 'red')
    else:
        return '?'
