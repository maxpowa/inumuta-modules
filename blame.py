# coding=utf8
"""
blame.py - Don't blame $nickname :V
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import rule


@rule('#?(die|blame|kill|beat|spit|hit|crash|batter|hammer|pound|thrash|bap|shoot|smack|whack|zap)(es|s)?[\s]*$nickname')
def blame(bot, trigger):
    bot.action('dies a little inside')
