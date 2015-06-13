# coding=utf8
"""
karma.py - maxpowa++
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import rate, rule, commands
from willie.tools import Identifier


@rate(10)
@rule(r'^([\S]+?)\+\+$')
def promote_karma(bot, trigger):
    """
    Update karma status for specify IRC user if get '++' message.
    """
    if (trigger.is_privmsg):
        return bot.say('People like it when you tell them good things.')
    if (bot.db.get_nick_id(Identifier(trigger.group(1))) == bot.db.get_nick_id(Identifier(trigger.nick))):
        return bot.say('You may not give yourself karma!')
    current_karma = bot.db.get_nick_value(trigger.group(1), 'karma')
    if not current_karma:
        current_karma = 0
    else:
        current_karma = int(current_karma)
    current_karma += 1

    bot.db.set_nick_value(trigger.group(1), 'karma', current_karma)
    bot.say(trigger.group(1) + ' == ' + str(current_karma))


@rate(10)
@rule(r'^([\S]+?)\-\-$')
def demote_karma(bot, trigger):
    """
    Update karma status for specify IRC user if get '--' message.
    """
    if (trigger.is_privmsg):
        return bot.say('Say it to their face!')
    if (bot.db.get_nick_id(Identifier(trigger.group(1))) == bot.db.get_nick_id(Identifier(trigger.nick))):
        return bot.say('You may not reduce your own karma!')
    current_karma = bot.db.get_nick_value(trigger.group(1), 'karma')
    if not current_karma:
        current_karma = 0
    else:
        current_karma = int(current_karma)
    current_karma -= 1

    bot.db.set_nick_value(trigger.group(1), 'karma', current_karma)
    bot.say(trigger.group(1) + ' == ' + str(current_karma))


@rate(10)
@rule(r'^([\S]+?)\=\=$')
def show_karma(bot, trigger):
    """
    Update karma status for specify IRC user if get '--' message.
    """
    current_karma = bot.db.get_nick_value(trigger.group(1), 'karma')
    if not current_karma:
        current_karma = 0
    else:
        current_karma = int(current_karma)

    bot.say(trigger.group(1) + ' == ' + str(current_karma))


@commands('karma')
def karma(bot, trigger):
    """Command to show the karma status for specify IRC user.
    """
    nick = trigger.nick
    if trigger.group(2):
        nick = trigger.group(2).strip().split()[0]

    karma = bot.db.get_nick_value(nick, 'karma')
    if not karma:
        karma = '0'
    bot.say("%s == %s" % (nick, karma))
