# coding=utf8
"""
logquery.py - Simple log query module
Copyright 2015 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import commands, rule, unblockable, event, thread, priority, OP
from datetime import datetime, date
import sqlite3
import re
import os

filename = 'logquery.db'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect():
    """Return a raw database connection object."""
    return sqlite3.connect(filename)


def _create():
    """Create the basic database structure."""
    # Do nothing if the db already exists.
    try:
        execute('SELECT * FROM logquery;')
    except:
        pass
    else:
        return

    execute('''CREATE TABLE IF NOT EXISTS logquery (
        id INTEGER PRIMARY KEY,
        channel TEXT,
        nick TEXT,
        ident TEXT,
        host TEXT,
        message TEXT,
        intent TEXT,
        sent_at TIMESTAMP
        )''')


def execute(*args, **kwargs):
    """Execute an arbitrary SQL query against the database.

    Returns a cursor object, on which things like `.fetchall()` can be
    called per PEP 249."""
    with connect() as conn:
        conn.row_factory = dict_factory
        cur = conn.cursor()
        return cur.execute(*args, **kwargs)


def setup(bot):
    global filename
    path = bot.config.logquery.filename
    config_dir, config_file = os.path.split(bot.config.filename)
    config_name, _ = os.path.splitext(config_file)
    if path is None:
        path = os.path.join(config_dir, 'logquery.db')
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.normpath(os.path.join(config_dir, path))
    filename = path
    _create()


@commands('disable-log')
def do_not_log(bot, trigger):
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return

    if not trigger.group(2):
        bot.reply('disable-log usage: .disable-log <true|false>')
        return

    if (trigger.group(2).strip().lower() == 'true'):
        bot.db.set_channel_value(trigger.sender, 'disable-log', True)
        execute('DELETE FROM logquery WHERE channel=?;', (trigger.sender, ))
        bot.say('No longer logging ' + trigger.sender)
    else:
        bot.db.set_channel_value(trigger.sender, 'disable-log', False)
        execute('DELETE FROM logquery WHERE channel=?;', (trigger.sender, ))
        bot.say('Logging ' + trigger.sender)


@commands('logquery')
def logquery(bot, trigger):
    base_query = None
    if trigger.group(2):
        base_query = re.findall(r'(first|last|count|show) where (.*)', trigger.group(2), re.I)  # The base command syntax. This /must/ match in order to query anything

    if not base_query:               # Return when invalid base command syntax used
        bot.say('[logquery] Usage: .logquery <first|last|count|show> where <nick|ident|host|message|channel|intent> =~ \'<glob>\' [<and|or> <nick|ident|host|message|channel|intent> =~ \'<glob>\']+')
        return

    query_log(bot, base_query[0])    # Grab the first tuple match and set that as the base query


@commands('logquery-util')
def lq_utils(bot, trigger):
    if not trigger.admin:           # If you aren't a bot admin, get outta this command!
        return
    if trigger.group(3) == 'clear':                                 # Clear the log
        execute('DELETE FROM logquery')
        bot.say('Cleared DB!')
        return


def query_log(bot, query):
    matches = []

    selector = '*'
    limit = 10
    if query[0].lower() == 'count':
        limit = 0
        selector = 'COUNT(*)'

    sql, params = construct_query(query[1], limit)
    try:
        c = execute('SELECT ' + selector + ' FROM (' + sql + ') ORDER BY datetime(sent_at) ASC', params)
        matches = c.fetchall()
    except Exception as e:
        bot.say('[logquery] Invalid query, try .logquery help for usage (' + e.message + ')')
        return

    if len(matches) == 0:                                                                   # No results, let the user know
        bot.say('[logquery] No results, try .logquery help for usage')
        return

    if query[0].lower() == 'count':                                                                 # Show the count
        bot.say(str(matches[0]['COUNT(*)']))
    elif query[0].lower() == 'first':                                                               # Show the first value in the list
        bot.say(format_msg(matches[0]))
    elif query[0].lower() == 'last':                                                                # Show the last value in the list
        bot.say(format_msg(matches[-1]))
    else:
        if len(matches) <= 5:                                                               # If it's less than 5 results, just dump 'em to chat
            for match in matches:
                bot.say(format_msg(match))
        else:                                                                               # Otherwise, only show the most recent 5
            bot.say('[logquery] Too many results, limiting to the most recent 5.')
            for match in matches[-5:]:
                bot.say(format_msg(match))


def construct_query(query, limit=10):
    sql = "SELECT * FROM logquery"
    where = []
    params = {}
    if (limit > 0):
        limit = 'LIMIT ' + str(limit)
    else:
        limit = ''

    for part in query.split('and'):
        # MUST match this regex, otherwise is not going to be used in the query
        adv_query = re.findall(r'(nick|ident|host|message|channel|intent) (=|\!)~ \'(.+?)\'', part, re.I)
        current = []
        for match in adv_query:
            if match is not None:
                key = match[0]
                while key in params:
                    key = key + "_"
                inverse = ''
                if match[1] == '!':
                    inverse = ' NOT'
                current.append(match[0] + inverse + " GLOB :" + key)
                params[key] = match[2]
        where.append(' OR '.join(current))

    if where:
        sql = '{} WHERE {} {}'.format(sql, ' AND '.join(where), 'GROUP BY sent_at ORDER BY datetime(sent_at) DESC ' + limit)
        return sql, params
    else:
        return "", ""


def format_msg(msg):
    """
    Format a SQL row to a nice IRC-like message
    """
    MESSAGE_TPL = "[{sent_at}] <{nick}/{channel}> {message}"
    ACTION_TPL = "[{sent_at}] * {nick}/{channel} {message}"
    NICK_TPL = "[{sent_at}] *** {nick} is now known as {message}"
    JOIN_TPL = "[{sent_at}] *** {nick} has joined {channel}"
    PART_TPL = "[{sent_at}] *** {nick} has left {channel} ({message})"
    QUIT_TPL = "[{sent_at}] *** {nick} has quit IRC ({message})"

    intent = msg['intent']
    msg['sent_at'] = msg['sent_at'].split(".")[0].split(" ")[1]
    if (intent == 'PRIVMSG'):
        return MESSAGE_TPL.format(**msg)
    elif (intent == 'ACTION'):
        return ACTION_TPL.format(**msg)
    elif (intent == 'NICK'):
        return NICK_TPL.format(**msg)
    elif (intent == 'JOIN'):
        return JOIN_TPL.format(**msg)
    elif (intent == 'PART'):
        return PART_TPL.format(**msg)
    elif (intent == 'QUIT'):
        return QUIT_TPL.format(**msg)

    return u'<{nick}/{channel}> {message}'.format(**msg)


@rule('.*')
@unblockable
def log_message(bot, message):
    "Log every message in a channel"
    # if this is a private message and we're not logging those, return early
    if message.sender.is_nick() or bot.db.get_channel_value(message.sender, 'disable-log'):
        return

    intent = 'PRIVMSG'
    if 'intent' in message.tags:
        intent = message.tags['intent']

    # Insert new text into table
    execute('INSERT INTO logquery (channel, nick, ident, host, message, intent, sent_at) VALUES (?,?,?,?,?,?,?)',
        (message.sender, message.nick, message.user, message.host, message.match.string, intent, datetime.utcnow()))

    # Ensure no more than x amount of messages exist for the current channel
    #execute('DELETE FROM logquery WHERE channel=? AND id NOT IN (SELECT id FROM logquery WHERE channel=? ORDER BY datetime(sent_at) DESC LIMIT 500)',
    #    (message.sender, message.sender))


@rule('.*')
@event("JOIN")
@unblockable
def log_join(bot, message):
    if message.sender.is_nick() or bot.db.get_channel_value(message.sender, 'disable-log'):
        return

    execute('INSERT INTO logquery (channel, nick, ident, host, message, intent, sent_at) VALUES (?,?,?,?,?,?,?)',
        (message.sender, message.nick, message.user, message.host, message.match.string, 'JOIN', datetime.utcnow()))


@rule('.*')
@event("PART")
@unblockable
def log_part(bot, message):
    if message.sender.is_nick() or bot.db.get_channel_value(message.sender, 'disable-log'):
        return

    execute('INSERT INTO logquery (channel, nick, ident, host, message, intent, sent_at) VALUES (?,?,?,?,?,?,?)',
        (message.sender, message.nick, message.user, message.host, message.match.string, 'PART', datetime.utcnow()))


@rule('.*')
@event("KICK")
@unblockable
def log_part(bot, message):
    if message.sender.is_nick() or bot.db.get_channel_value(message.sender, 'disable-log'):
        return

    execute('INSERT INTO logquery (channel, nick, ident, host, message, intent, sent_at) VALUES (?,?,?,?,?,?,?)',
        (message.sender, message.nick, message.user, message.host, message.match.string, 'KICK', datetime.utcnow()))


@rule('.*')
@event("MODE")
@unblockable
def log_mode(bot, message):
    if message.sender.is_nick() or bot.db.get_channel_value(message.sender, 'disable-log'):
        return

    execute('INSERT INTO logquery (channel, nick, ident, host, message, intent, sent_at) VALUES (?,?,?,?,?,?,?)',
        (message.sender, message.nick, message.user, message.host, ' '.join(message.args[1:]), 'MODE', datetime.utcnow()))


@rule('.*')
@event("QUIT")
@unblockable
@thread(False)
@priority('high')
def log_quit(bot, message):
    if message.sender.is_nick() or bot.db.get_channel_value(message.sender, 'disable-log'):
        return

    time = datetime.utcnow()
    # make a copy of bot.privileges that we can safely iterate over
    privcopy = list(bot.privileges.items())
    # write logline to *all* channels that the user was present in
    for channel, privileges in privcopy:
        if message.nick in privileges:
            execute('INSERT INTO logquery (channel, nick, ident, host, message, intent, sent_at) VALUES (?,?,?,?,?,?,?)',
                (channel, message.nick, message.user, message.host, message.match.string, 'QUIT', time))


@rule('.*')
@event("NICK")
@unblockable
def log_nick_change(bot, message):
    time = datetime.utcnow()
    old_nick = message.nick
    new_nick = message.sender
    # make a copy of bot.privileges that we can safely iterate over
    privcopy = list(bot.privileges.items())
    # write logline to *all* channels that the user is present in
    for channel, privileges in privcopy:
        if old_nick in privileges or new_nick in privileges:
            execute('INSERT INTO logquery (channel, nick, ident, host, message, intent, sent_at) VALUES (?,?,?,?,?,?,?)',
                (channel, old_nick, message.user, message.host, new_nick, 'NICK', time))
