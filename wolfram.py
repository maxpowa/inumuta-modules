# coding=utf8

from __future__ import unicode_literals
from willie.module import commands
from willie import web
import tungsten
import json


output_ids = ['DecimalApproximation', 'Result', 'ExactResult']


@commands('wa', 'wolfram')
def wa_query(bot, trigger):
    if not trigger.group(2):
        return bot.say('[Wolfram] You must provide a query')
    client = tungsten.Tungsten(bot.config.wolfram.app_id)

    try:
        result = client.query(trigger.group(2))
    except Exception as e:
        return bot.say('[Wolfram] An error occurred ({})'.format(e.message))

    for pod in result.pods:
        if pod.id not in output_ids:
            continue
        return bot.say('{}: {}'.format(pod.title, pod.format['plaintext'][0]))

    if len(result.pods) > 0:
        return bot.say('[Wolfram] No text-representable result found, see http://wolframalpha.com/input/?i={}'.format(web.quote(trigger.group(2))))

    return bot.say('[Wolfram] No results found.')
