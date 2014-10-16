#!/usr/bin/env python
# encoding: utf-8

"""
karma.py - A karma module for willie.
Copyright 2014 Max Gurela
Copyright 2013, Timothy Lee <marlboromoo@gmail.com>
Licensed under the MIT License.
"""

import string
import willie

###############################################################################
# Setup the module
###############################################################################

MODULE = 'karma'
WHO = 'who'
KARMA = 'karma'
REASON = 'reason'
DEBUG_LEVEL = 'verbose'

feedback = None
byself = None

def debug_(tag, text, level):
    """Mimic willie.debug function for pytest to use.
    """
    print "[%s] %s" % (tag, text)

debug = debug_

def configure(config):
    """

    | [karma] | example | purpose |
    | ------- | ------- | ------- |
    | feedback | True | Notify by bot |
    | byself | False | Self (pro|de)mote |

    """
    if config.option('Configure karma', False):
        config.interactive_add('karma', 'feedback', 'Notify by bot', 'True')
        config.interactive_add('karma', 'byself', 'Self (pro|de)mote', 'False')

def setup(bot):
    """Setup the database, get the settings.

    :bot: willie.bot.Willie

    """
    #. get debug function
    global debug
    debug = bot.debug if bot.debug else debug
    #. get settings
    feedback_, byself_, debug_ = True, False, False
    try:
        config = getattr(bot.config, MODULE)
        feedback_ = is_true(config.feedback)
        byself_ = is_true(config.byself)
    except Exception, e:
        pass
    global feedback, byself
    feedback = feedback_
    byself = byself_

    #. check database
    if bot.db:
        key, name = WHO, KARMA
        columns = [key, KARMA, REASON]
        if not getattr(bot.db, name):
                try:
                    bot.db.add_table(name, columns, key)
                except Exception, e:
                    debug(MODULE, 'Table init fail - %s' % (e), DEBUG_LEVEL)
                    raise e
    else:
        msg = "DB init fail, setup the DB first!"
        debug(MODULE, msg, DEBUG_LEVEL)
        raise Exception(msg)

###############################################################################
# Helper function
###############################################################################

def is_true(value):
    """Return True if value is true

    :value: value
    :returns: True or False

    """
    try:
        return True if  value.lower() == 'true' else False
    except Exception:
        return value

def get_table(bot):
    """Return the table instance.

    :bot: willie.bot.Willie
    :returns: willie.db.Table

    """
    try:
        return getattr(bot.db, KARMA)
    except Exception:
        return None

def get_karma(table, who):
    """Get karma status from the table.

    :table: willie.db.Table instance
    :who: nickname of IRC user
    :returns: (karma, reason)

    """
    karma, reason = str(0), str(None)
    try:
        karma, reason = table.get(who, (KARMA, REASON))
    except Exception, e:
        debug(MODULE, "get karma fail - %s." % (e), DEBUG_LEVEL)
    return karma, reason

def _update_karma(table, who, reason, method='+'):
    """Update karma for specify IRC user.

    :table: willie.db.Table
    :who: nickname of IRC user
    :reason: reason
    :method: '+' or '-'

    """
    karma = get_karma(table, who)[0]
    karma = int(karma) if karma else 0
    try:
        if method == '+':
            table.update(who, dict(karma=str(karma + 1), reason=reason))
        else:
            table.update(who, dict(karma=str(karma - 1), reason=reason))
    except Exception, e:
        debug(MODULE, "update karma fail, e: %s" % (e), DEBUG_LEVEL)

def promote_karma(table, who, reason):
    """Promote karma for specify IRC user.

    :table: willie.db.Table
    :who: nickname of IRC user
    :reason: reason

    """
    return _update_karma(table, who, reason, '+')

def demote_karma(table, who, reason):
    """Demote karma for specify IRC user.

    :table: willie.db.Table
    :who: nickname of IRC user
    :reason: reason

    """
    return _update_karma(table, who, reason, '-')

def _parse_msg(msg, method='+'):
    """Parse the message.

    :msg: message
    :returns: (who, reason)

    """
    try:
        who = msg.split(method)[0].strip().split().pop()
        reason = msg.split(method)[2].strip()
        if '#' in reason:
            reason = reason.split('#')[1].strip()
        if len(reason) == 0:
            reason = None
        #. strip illegal chars
        reason = reason.replace('"', '') if reason else reason
    except Exception, e:
        debug(MODULE, "parse message fail - %s." % (e), DEBUG_LEVEL)
        return None, None
    return who, reason

def parse_promote(msg):
    """Parse the message with '++'.

    :msg: message
    :returns: (who, reason)

    """
    return _parse_msg(msg, method='+')

def parse_demote(msg):
    """Parse the message with '--'.

    :msg: message
    :returns: (who, reason)

    """
    return _parse_msg(msg, method='-')

def meet_karma(bot, trigger, parse_fun, karma_fun):
    """Update karma status for specify IRC user

    :bot: willie.bot.Willie
    :trigger: willie.bot.Willie.Trigger

    """
    table = get_table(bot)
    if table:
        msg = trigger.bytes
        who, reason = parse_fun(msg)
        if who:
            #. not allow self (pro|de)mote
            if not byself:
                if who == trigger.nick:
                    return
            #. update karma
            reason = reason if reason else str(None)
            karma_fun(table, who, reason)
            karma, reason= get_karma(table, who)
            if feedback:
                bot.say("%s=%s" % (who, karma))

###############################################################################
# Event & Command
###############################################################################

@willie.module.rule(r'^[\w][\S]+[\+\+]$')
def meet_promote_karma(bot, trigger):
    """Update karma status for specify IRC user if get '++' message.
    """
    return meet_karma(bot, trigger, parse_promote, promote_karma)

@willie.module.rule(r'^[\w][\S]+[\-\-]$')
def meet_demote_karma(bot, trigger):
    """Update karma status for specify IRC user if get '--' message.
    """
    return meet_karma(bot, trigger, parse_demote, demote_karma)

@willie.module.commands('karma')
def karma(bot, trigger):
    """Command to show the karma status for specify IRC user.
    """
    table = get_table(bot)
    if table:
        if trigger.group(2):
            who = trigger.group(2).strip().split()[0]
            karma, reason= get_karma(table, who)
            bot.say("%s == %s" % (who, karma))
        else:
            bot.say(".karma <nick> - Reports karma status for <nick>.")
    else:
        bot.say("Setup the database first, contact your bot admin.")

