"""
ooclan.py - GG Bot
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import rule, rate
import random


@rate(600)
@rule('^([^\<].+) (?:went up in flames|burned to death|tried to swim in lava|suffocated in a wall|drowned|starved to death|was pricked to death|hit the ground too hard|fell out of the world|died|blew up|was killed by magic|was slain by (.+)|was shot by (.+)|was fireballed by (.+)|was pummeled by (.+)|was killed by (.+))$')
def death_event(bot, trigger):
    if not (trigger.nick == 'JamOORev') or (trigger.nick == 'JamOORevLite'):
        return
    else:
        opts = [
            'https://www.youtube.com/watch?v=5es0NNtSNCU',
            'http://i.imgur.com/FqLvsiE.jpg'
        ]
        bot.say('gg ' + trigger.group(1).strip()[:1] + u'\u0081' + trigger.group(1).strip()[1:] + ', ' + random.choice(opts))
