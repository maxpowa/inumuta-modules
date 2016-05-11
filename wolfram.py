# coding=utf8

from __future__ import unicode_literals
from willie.module import commands
from willie import web
import tungsten
import json

@commands('wa', 'wolfram')
def wa_query(bot, trigger):
    if not trigger.group(2):
        return bot.say('[Wolfram] You must provide a query')
    client = tungsten.Tungsten(bot.config.wolfram.app_id)

    try:
        result = client.query(trigger.group(2))
    except Exception as e:
        return bot.say('[Wolfram] An error occurred ({})'.format(e.message))

    if len(result.pods) < 2:
        return bot.say('[Wolfram] No text-representable result found, see http://wolframalpha.com/input/?i={}'.format(web.quote(trigger.group(2))))

    query = result.pods[0]
    response = result.pods[1]
    return bot.say('{}: {}'.format(query.format['plaintext'][0], response.format['plaintext'][0]))
