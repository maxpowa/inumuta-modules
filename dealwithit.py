# coding=utf8
"""
dealwithit.py - Just deal with it.
Copyright 2014, Max Gurela http://everythingisawesome.us

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands
import random


@commands('dealwithit', 'deal')
def deal_with_it(bot, trigger):
    """
    .dealwithit
    """
    messages = ['http://i.imgur.com/Tuivz2O.gif', 'http://i.imgur.com/pbQmk.gif', 'http://i.imgur.com/eGInc.jpg', 'http://i.imgur.com/Wa1Cf8E.gif', 'http://i.imgur.com/CxhomG0.gif']
    if trigger.group(2):
        bot.say(trigger.group(2).strip() + ': ' + random.choice(messages))
    else:
        bot.reply(random.choice(messages))
