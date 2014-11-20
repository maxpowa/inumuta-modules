# coding=utf8
"""
logquery.py - Simple log query module (replaces log_raw, so there may be incompatibility with other modules that do so)
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

import time
import os
import codecs
import re
import socket

from willie.irc import Bot
from willie.module import commands, OP
from willie.tools import stderr

from collections import deque

#MATCH FORMAT: nick | hostname | message type | source | content
MATCH = re.compile(r':(.+)!(.+) (PRIVMSG|NOTICE) (.+) :(.+)')
BOT_MATCH = re.compile(r'(PRIVMSG|NOTICE) (.+) :(.+)')
HOSTNAME = socket.getfqdn() #Closest we are going to get to determining the current hostname
HOSTMASK = '~this@is.wrong'
MAX_LENGTH = 500
bot_log = True
messages = deque()

def setup(bot):
    global HOSTMASK, HOSTNAME, messages, LOG_DIR, MAX_LENGTH
    messages = deque()
    LOG_DIR = os.path.join(bot.config.core.logdir, 'logquery')
    print('[logquery] Inserting modded log_raw')
    Bot.log_raw = log_raw_mod
    print('[logquery] Success! Loading previous text lines')
    read_messages(bot)
    HOSTMASK = '~'+bot.config.core.user+'@'+HOSTNAME
    print('[logquery] Hostname configured as '+HOSTMASK)

def shutdown(bot):
    global messages
    print('[logquery] Inserting vanilla log_raw')
    Bot.log_raw = log_raw
    print('[logquery] Success! Saving previous text lines')
    save_messages(bot)

@commands('logquery')
def logquery(bot, trigger):
    global bot_log
    base_query = re.findall(r'(count|show) where (.*)', trigger.group(2), re.I)
    
    if not base_query:
        bot.say('[logquery] Usage: .logquery <count|show> where <nick|hostmask|content|source|type> =~ \'<regex>\' [<and|or> <nick|hostmask|content|source|type> =~ \'<regex>\']+')
        return
        
    base_query = base_query[0]
    initial = True
    matches = []
        
    for part in base_query[1].split('and'):
        adv_query = re.findall(r'(nick|hostmask|content|source) =~ \'(.+?)\'', part, re.I)
        for match in adv_query:
            if initial:
                bot_log = False
                for msg in messages:
                    if re.search(match[1], msg[match[0]]):
                        if not msg in matches:
                            matches.append(msg)
                bot_log = True
            else:
                temp = []
                for msg in matches:
                    if re.search(match[1], msg[match[0]]):
                        if not msg in temp:
                            temp.append(msg)
                matches = temp
        initial = False
    
    if base_query[0] == 'count':
        bot.say(str(len(matches)))
    else:
        if len(matches) == 0:
            bot.say('[logquery] No results')
        elif len(matches) <= 5:
            for match in matches:
                bot.say(format_msg(match))
        else:
            bot.say('[logquery] Too many results, limiting to the most recent 5.')
            for match in matches[-5:]:
                bot.say(format_msg(match))
    
@commands('logquery-util')
def lq_utils(bot, trigger):
    global bot_log, messages
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    if trigger.group(3) == 'stats':
        bot.say('Total Messages: '+str(len(messages)))
        return
    if trigger.group(3) == 'save':
        save_messages(bot)
        return
    if trigger.group(3) == 'clear':
        messages = deque()
        save_messages(bot)
        return
    if trigger.group(3) == 'dump':
        bot_log = False
        for msg in messages:
            bot.notice(parse_msg(msg), recipient=trigger.nick)
        bot_log = True
        
def format_msg(msg):
    return u'<{}/{}> {}'.format(msg['nick'], msg['source'], msg['content'])

def save_messages(bot):
    global messages
    try:
        os.mkdir(LOG_DIR)
    except:
        """ HUSH CHILD """
    f = codecs.open(os.path.join(LOG_DIR, 'msg.log'), 'w', encoding='utf-8')
    for msg in messages:
        f.write(parse_msg(msg))
        f.write('\n')
    f.close()
    print('[logquery] Saved')
    
def read_messages(bot):
    try:
        f = codecs.open(os.path.join(LOG_DIR, 'msg.log'), 'r', encoding='utf-8')
        for line in f:
            try_parse_line(line)
        f.close()
    except IOError:
        print('[logquery] Unable to read msg.log (usual for first run)')
    print('[logquery] Done loading.')
    
""" PARSING """
def parse_msg(msg):
    return u':{}!{} {} {} :{}'.format(msg['nick'], msg['hostmask'], msg['type'], msg['source'], msg['content'])

def try_parse_line(line):
    result = MATCH.match(line)
    if result:
        parse_line(result)

def parse_line(match):
    global messages
    if len(messages) >= MAX_LENGTH:
        messages.popleft()
    content = {'nick': match.group(1), 'hostmask': match.group(2), 'type': match.group(3), 'source': match.group(4), 'content': match.group(5)}
    if not content in messages:
        messages.append(content)

def parse_bot_line(nick, match):
    global messages
    if len(messages) >= MAX_LENGTH:
        messages.popleft()
    content = {'nick': nick, 'hostmask': HOSTMASK, 'type': match.group(1), 'source': match.group(2), 'content': match.group(3)}
    if not content in messages:
        messages.append(content)

""" END PARSING """
    
def log_raw_mod(self, line, prefix):
    """Log raw line to the raw log."""
    log_raw(self, line, prefix)
    if bot_log:
        log_msg(self, line, prefix) # Handle the line 

def log_msg(self, line, prefix):
    result = MATCH.match(line)
    if result:
        parse_line(result)
        return
    result = BOT_MATCH.match(line)
    if result:
        parse_bot_line(self.config.core.nick, result)
    
""" 
Vanilla willie raw_log code 
"""
def log_raw(self, line, prefix):
    if not self.config.core.log_raw:
        return
    if not self.config.core.logdir:
        self.config.core.logdir = os.path.join(self.config.dotdir, 'logs')
    if not os.path.isdir(self.config.core.logdir):
        try:
            os.mkdir(self.config.core.logdir)
        except Exception as e:
            stderr('There was a problem creating the logs directory.')
            stderr('%s %s' % (str(e.__class__), str(e)))
            stderr('Please fix this and then run Willie again.')
            os._exit(1)
    f = codecs.open(os.path.join(self.config.core.logdir, 'raw.log'), 'a', encoding='utf-8')
    f.write(prefix + unicode(time.time()) + "\t")
    temp = line.replace('\n', '')

    f.write(temp)
    f.write("\n")
    f.close()
"""
End Vanilla willie raw_log code
"""
