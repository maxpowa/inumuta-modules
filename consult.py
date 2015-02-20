# coding=utf8
"""
consult.py - Consult Inumuta about anything
Copyright 2014, Max Gurela http://everythingisawesome.us

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import commands
import random


@commands('consult')
def consult(bot, trigger):
    """
    .consult <question> - Consult Inumuta about anything
    """
    messages = ['Yes.', 'No.', 'Maybe.', 'Go ask Google.', 'Why not?', 'I don\'t know.', 'Ask someone else.', 'Why would you ask that?', 'Nobody knows...', 'I would advise against it.', 'No way!', 'Never.', 'Try another question.', 'If you feel like it.', 'Go for it!', 'Bad idea.', '42', '2147483647', 'Error: Query provided cannot be answered.', 'It\'s up to you.']
    bot.say(random.choice(messages))
