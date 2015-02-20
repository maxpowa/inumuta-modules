# coding=utf8
"""
esper.py - An esper is an individual capable of telepathy and other similar paranormal abilities
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import commands, rule, event, unblockable
from willie.tools import Identifier

force = {}


@commands('alias')
def check_alias(bot, trigger):
    if not trigger.group(3):
        bot.reply('alias usage: .alias <add|merge|list>')
        return

    if (trigger.group(3).lower() == 'add'):
        bot.write(['PRIVMSG', 'NickServ', ':info', trigger.nick])
        bot.reply('Fetching NickServ info... I will get back to you in a PM')

    elif (trigger.group(3).lower() == 'merge'):
        force[trigger.nick] = True
        bot.write(['PRIVMSG', 'NickServ', ':info', trigger.nick])
        bot.reply('Fetching NickServ info... I will get back to you in a PM')

    elif (trigger.group(3).lower() == 'list'):
        try:
            alias = Identifier(trigger.nick)
            nick_id = bot.db.get_nick_id(alias, False)
            nicks = bot.db.execute('SELECT DISTINCT canonical FROM nicknames WHERE nick_id = ?', [nick_id]).fetchall()
            bot.say('{}, your aliases are: {}'.format(trigger.nick, ' '.join([nick[0] for nick in nicks])))
        except:
            bot.say('Something went wrong, perhaps you haven\'t aliased any nicks?')


@rule('^Information on (.+) \(account (.+)\):$')
@event("NOTICE")
@unblockable
def receive_info(bot, trigger):
    if trigger.sender != 'NickServ':
        return

    account = Identifier(trigger.group(2))
    nick = Identifier(trigger.group(1))

    try:
        bot.db.alias_nick(account, nick)
    except ValueError as e:
        try:
            bot.db.alias_nick(nick, account)
        except ValueError as e:
            if nick in force:
                bot.db.merge_nick_groups(account, nick)
                first_id = bot.db.get_nick_id(Identifier(account))
                second_id = bot.db.get_nick_id(Identifier(nick))
                bot.db.execute('UPDATE nicknames SET nick_id = ? WHERE nick_id = ?',
                     [first_id, second_id])
                bot.msg(nick, 'Merged {0} and {1}. If conflicting values were found' \
                    ' between accounts, values from {0} were used.'.format(account, nick))
                del force[nick]
            else:
                extra = ''
                if nick.lower() != account.lower():
                    extra = 'If you wish to merge data' \
                    ' from {0} to {1}, you may do so by using `.alias merge`. Please note that doing so' \
                    ' will overwrite conflicting values with those found in {0}. '.format(account, nick)
                bot.msg(nick, 'Sorry, I was unable to alias your nick' \
                    ' to your account -- it might have already been aliased. {1}({0})'.format(e.message, extra))
                return

    bot.msg(nick, 'Successfully aliased ' + nick + ' to account ' + account)
