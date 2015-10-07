# coding=utf8
"""
invite.py - Invite all the things
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands, event, rule, priority, OP, interval


def setup(bot):
    """
    Auto-join invited channels
    """
    try:
        cursor = bot.db.execute('SELECT DISTINCT channel FROM channel_values')
    except:
        return
    for channel in cursor.fetchall():
        try:
            channel = str(channel[0])
            if bot.db.get_channel_value(channel, 'autojoin'):
                print('[invite] Joining ' + channel)
                bot.join(channel)
        except:
            pass


@interval(60 * 30)
def keep_joined(bot):
    setup(bot)


@event('INVITE')
@rule('.*')
@priority('low')
def invite_join_chan(bot, trigger):
    """
    Join a channel Inumuta is invited to, allows plebs to have the bot in their chan.
    """
    if trigger.admin:
        return

    restrictor = bot.db.get_channel_value(trigger.args[1], 'restricted-by')
    if restrictor:
        if not restrictor == trigger.nick:
            bot.msg(trigger.nick, 'Sorry, {0} has requested that I do not join {1}. I will not join unless I '
                                  'am invited by {0}.'.format(restrictor, trigger.args[1]))
            return
        else:
            bot.db.set_channel_value(trigger.args[1], 'restricted-by', None)

    if trigger.args[1].lower() in [chan.lower() for chan in bot.channels]:
        return

    bot.join(trigger.args[1])
    bot.db.set_channel_value(trigger.args[1], 'autojoin', True)
    bot.msg(trigger.args[1], 'Hi {}! I was invited by {}. If you need assistance, please use \'.help\'. I may respond to other '
                             'bots in specific circumstances, though I will prevent myself from repeating the same message 6 '
                             'times in a row. By default, I log any messages sent in channels I\'m in. If you don\'t want me '
                             'to log this channel, please have a chanop say \'.disable-log true\' and I will stop logging '
                             'this channel.'.format(trigger.args[1], trigger.nick))
    bot.msg(trigger.args[1], 'If my presence is unwanted, simply have a chanop say \'.part\' and I will gladly leave you alone.')


@commands('part')
@priority('low')
def part_chanop(bot, trigger):
    if trigger.admin:
        bot.db.set_channel_value(trigger.sender, 'autojoin', False)
        return

    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return

    bot.part(trigger.sender, 'Part requested by {}'.format(trigger.nick))
    bot.db.set_channel_value(trigger.sender, 'autojoin', False)
    bot.db.set_channel_value(trigger.sender, 'restricted-by', trigger.nick)


@commands('channels')
def chanlist(bot, trigger):
    if not trigger.admin:
        return
    bot.say('My connected channels ({}): {}'.format(len(bot.channels), ', '.join(bot.channels)))
