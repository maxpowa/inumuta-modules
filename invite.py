# coding=utf8
"""
invite.py - Invite all the things
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands, event, rule, priority, OP

restricted_channels = {}

@event('INVITE')
@rule('.*')
@priority('low')
def invite_join_chan(bot, trigger):
    global restricted_channels
    """
    Join a channel Inumuta is invited to, allows plebs to have the bot in their chan.
    """
    if trigger.admin:
	return

    if trigger.args[1].lower() in restricted_channels:
        if not restricted_channels[trigger.args[1].lower()] == trigger.nick:    
            bot.msg(trigger.nick, 'Sorry, {} has requested that I do not join {}. I will not join unless I am invited by {}.'.format(restricted_channels[trigger.args[1].lower()], trigger.args[1], restricted_channels[trigger.args[1].lower()]))
            return
        else:
            del restricted_channels[trigger.args[1].lower()]

    if trigger.args[1].lower() in [chan.lower() for chan in bot.channels]:
        return

    bot.join(trigger.args[1])
    bot.msg(trigger.args[1], 'Hi {}! I was invited by {}. If you need assistance, please use \'.help\'. I may respond to other bots in specific circumstances, though I will prevent myself from repeating the same message 6 times in a row. If my presence is unwanted, simply have a chanop say \'.part\' and I will gladly leave you alone.'.format(trigger.args[1], trigger.nick))

@commands('part')
@priority('low')
def part_chanop(bot, trigger):
    global restricted_channels
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return

    bot.part(trigger.sender, 'Part requested by {}'.format(trigger.nick))
    restricted_channels[trigger.sender.lower()] = trigger.nick

@commands('channels')
def chanlist(bot, trigger):
    bot.say('My connected channels: '+', '.join(bot.channels))
    
