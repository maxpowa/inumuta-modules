# coding=utf8
"""
logquery.py - Simple log query module (replaces log_raw, so there may be incompatibility with other modules that do so)
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands, rule, unblockable
from datetime import datetime
import sqlite3
import re

def setup(bot):
    conn = bot.db.connect()
    c = conn.cursor()

    try:
        c.execute('SELECT * FROM logquery')
    except StandardError:
        create_table(bot, c)
        conn.commit()
    conn.close()


def create_table(bot, c):
    c.execute('''CREATE TABLE IF NOT EXISTS logquery (
        id INTEGER PRIMARY KEY,
        channel TEXT,
        nick TEXT,
        ident TEXT,
        host TEXT,
        message TEXT,
        intent TEXT,
        sent_at TIMESTAMP
        )''')

@rule('.*')
@unblockable
def log_message(bot, message):
    "Log every message in a channel"
    # if this is a private message and we're not logging those, return early
    if message.sender.is_nick():
        return

    intent = 'PRIVMSG'
    if 'intent' in message.tags:
        intent = message.tags['intent']

    conn = bot.db.connect()
    c = conn.cursor()

    # Insert new text into table
    c.execute('INSERT INTO logquery (channel, nick, ident, host, message, intent, sent_at) VALUES (?,?,?,?,?,?,?)',
        (message.sender, message.nick, message.user, message.host, message.match.string, intent, datetime.now()))

    # Ensure no more than x amount of messages exist for the current channel
    c.execute('DELETE FROM logquery WHERE channel=? AND id NOT IN (SELECT id FROM logquery WHERE channel=? ORDER BY datetime(sent_at) DESC LIMIT 500)',
        (message.sender, message.sender))

    conn.commit()
    conn.close()

@commands('logquery')
def logquery(bot, trigger):
    base_query = None
    if trigger.group(2):
        base_query = re.findall(r'(first|last|count|show) where (.*)', trigger.group(2), re.I)  # The base command syntax. This /must/ match in order to query anything

    if not base_query:               # Return when invalid base command syntax used
        bot.say('[logquery] Usage: .logquery <first|last|count|show> where <nick|ident|host|message|channel|intent> =~ \'<regex>\' [<and|or> <nick|ident|host|message|channel|intent> =~ \'<regex>\']+')
        return

    query_log(bot, base_query[0])    # Grab the first tuple match and set that as the base query

def query_log(bot, query):
    matches = []

    conn = bot.db.connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(*construct_query(query[1]))
    matches = c.fetchall()

    conn.commit()
    conn.close()

    if len(matches) == 0:                                                                   # No results, let the user know
        bot.say('[logquery] No results, try .logquery help for usage')
        return

    if query[0] == 'count':                                                                 # Show the count
        bot.say(str(len(matches)))
    elif query[0] == 'first':                                                               # Show the first value in the list
        bot.say(format_msg(matches[0]))
    elif query[0] == 'last':                                                                # Show the last value in the list
        bot.say(format_msg(matches[-1]))
    else:
        if len(matches) <= 5:                                                               # If it's less than 5 results, just dump 'em to chat
            for match in matches:
                bot.say(format_msg(match))
        else:                                                                               # Otherwise, only show the most recent 5
            bot.say('[logquery] Too many results, limiting to the most recent 5.')
            for match in matches[-5:]:
                bot.say(format_msg(match))

def construct_query(query):
    sql = "SELECT * FROM logquery"
    where = []
    params = {}

    for part in query.split('and'):
        # MUST match this regex, otherwise is not going to be used in the query
        adv_query = re.findall(r'(nick|ident|host|message|channel|intent) =~ \'(.+?)\'', part, re.I)
        current = []
        for match in adv_query:
            if match is not None:
                key = match[0]
                while key in params:
                    key = key+"_"
                current.append(match[0]+" GLOB :"+key)
                params[key] = match[1]
        where.append(' OR '.join(current))

    if where:
        sql = '{} WHERE {} {}'.format(sql, ' AND '.join(where), 'ORDER BY datetime(sent_at) ASC')
        return sql, params
    else:
        return "", ""

def format_msg(msg):
    """
    Format a SQL row to a nice IRC-like message
    """
    return u'<{}/{}> {}'.format(msg['nick'], msg['channel'], msg['message'])
