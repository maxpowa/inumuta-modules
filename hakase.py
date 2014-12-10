"""
hakase.py - HAKASEHAKASEHAKASEHAKASE
Copyright 2014, Max Gurela http://everythingisawesome.us

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands

@commands('hakase', 'hakasie', 'nano')
def nano_hakase(bot, trigger):
    """
    Nano: HAKASEHAKASEHAKASEHAKASE
    Hakase: NANONANONANONANO
    """
    if trigger.group(2):
        bot.say(trigger.group(2).strip() + ': https://www.youtube.com/embed/5MJQhe6XdWg?autoplay=1')
    else:
        bot.reply('https://www.youtube.com/embed/5MJQhe6XdWg?autoplay=1')
