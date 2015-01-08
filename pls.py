# coding=utf8
"""
pls.py - Count pls

Licensed under the Eiffel Forum License 2.
"""

import re
import time
import datetime
from willie.tools import get_timezone, format_time
from willie.tools import Nick, WillieMemory
from willie.module import rule, priority, commands, interval

def setup(bot):
    bot.memory['pls_count'] = WillieMemory()
    bot.memory['pls_count_time'] = time.time()

@rule('(.*pls.*)')
@priority('low')
def collectpls(bot, trigger):
    """Count times users say pls """
    
    if trigger.is_privmsg:
        return

    if trigger.group(1):
        if '.plscount' in trigger.group(1):
            return
        
    # Add a count for the channel and nick, if there isn't already one
    if trigger.sender not in bot.memory['pls_count']:
        bot.memory['pls_count'][trigger.sender] = WillieMemory()
    if Nick(trigger.nick) not in bot.memory['pls_count'][trigger.sender]:
        bot.memory['pls_count'][trigger.sender][Nick(trigger.nick)] = 0

    # Count them
    count = bot.memory['pls_count'][trigger.sender][Nick(trigger.nick)]
    count += 1
    bot.memory['pls_count'][trigger.sender][Nick(trigger.nick)] = count

@commands('plscount')
def format_count(bot, trigger):
    if trigger.is_privmsg:
        return

    user = Nick(trigger.group(2) or trigger.nick)
    
    user = Nick(user.strip())
    
    count = get_count(bot, user, trigger.sender)
    since = bot.memory['pls_count_time']
    
    timezone = get_timezone(bot.db, bot.config, None, trigger.nick)
    if not timezone:
        timezone = 'UTC'
    time = format_time(bot.db, bot.config, timezone, trigger.nick, trigger.sender, datetime.datetime.fromtimestamp(since))
    
    bot.say('{} has said pls in {} {} time(s) since {}'.format(user, trigger.sender, count, time))
    
@interval(3600 * 24)
def reset(bot, trigger):
    setup(bot)
    
def get_count(bot, user, chan):
    chan_count = bot.memory['pls_count']
    # only do something if there is conversation to work with
    if chan not in chan_count:
        return 0
    if Nick(user) not in chan_count[chan]:
        return 0
        
    return chan_count[chan][Nick(user)]