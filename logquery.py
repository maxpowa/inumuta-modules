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
from willie.module import commands, interval, OP
from willie.tools import stderr

from collections import deque

# This message is from irc users (incoming)
# :maxpowa!~maxpowa@irc.everythingisawesome.us PRIVMSG #WAMM :wooo
MATCH = re.compile(r':(.+)!(.+) (PRIVMSG|NOTICE) (.+) :(.+)')

# This message is from the bot iself (outgoing)
# PRIVMSG #WAMM :wooo
BOT_MATCH = re.compile(r'(PRIVMSG|NOTICE) (.+) :(.+)')

# Closest we are going to get to determining the current hostname
HOSTNAME = socket.getfqdn()

# This is replaced in module.setup
HOSTMASK = '~youve@done.something.very.wrong'

# Max message history to store (across all connected channels)
MAX_LENGTH = 500

# True to pause logging (while dumping or searching) and False to continue
PAUSE_LOG = False

# Considering splitting this into a dict of deque, so each channel can have its own history length
messages = deque()

def setup(bot):
    global HOSTMASK, HOSTNAME, messages, LOG_DIR, MAX_LENGTH
    
    messages = deque()                                          # Reset messages array
    LOG_DIR = os.path.join(bot.config.core.logdir, 'logquery')  # Initialize LOG_DIR directory
    
    #TODO: Load MAX_LENGTH from config section
    
    print('[logquery] Inserting modded log_raw')                
    Bot.log_raw = log_raw_mod                                   # Replace log_raw method in Bot class to intercept messages
    print('[logquery] Modded log_raw successfully injected')   
    
    HOSTMASK = '~'+bot.config.core.user+'@'+HOSTNAME            # Initialize hostname
    print('[logquery] Hostname configured as '+HOSTMASK)        
    
    read_messages(bot)                                          # Read previous messages from log

def shutdown(bot):
    global messages
    
    print('[logquery] Reverting log_raw changes')
    Bot.log_raw = log_raw                                       # Put back original log_raw
    print('[logquery] Vanilla log_raw successfully injected')
    
    save_messages(bot)                                          # Save past messages to log

@commands('logquery')
def logquery(bot, trigger):
    global PAUSE_LOG
    
    base_query = re.findall(r'(first|last|count|show) where (.*)', trigger.group(2), re.I)  # The base command syntax. This /must/ match in order to query anything
    
    if not base_query:               # Return when invalid base command syntax used
        bot.say('[logquery] Usage: .logquery <first|last|count|show> where <nick|hostmask|content|source|type> =~ \'<regex>\' [<and|or> <nick|hostmask|content|source|type> =~ \'<regex>\']+')
        return
        
    query_log(bot, base_query[0])    # Grab the first tuple match and set that as the base query
    
@commands('logquery-util')
def lq_utils(bot, trigger):
    global PAUSE_LOG, messages
    if bot.privileges[trigger.sender][trigger.nick] < OP:           # If you aren't a bot OP, get outta this command!
        return
    if trigger.group(3) == 'stats':                                 # Check message stats
        bot.say('Total Messages: '+str(len(messages)))
        return
    if trigger.group(3) == 'save':                                  # Save bot log to file
        save_messages(bot)
        return
    if trigger.group(3) == 'clear':                                 # Clear the log
        messages = deque()
        save_messages(bot)
        return
    if trigger.group(3) == 'dump':                                  # Dump all messages (will most likely result in flood kick)
        PAUSE_LOG = True
        for msg in messages:
            bot.notice(parse_msg(msg), recipient=trigger.nick)
        PAUSE_LOG = False
        
@interval(900)
def autosave(bot):
    save_messages(bot)
    return
    
def query_log(bot, query):
    first_pass = True                                                                       # Store whether this pass is the first or not
    matches = []                                                                            # Store matching messages
    
    """ Start parsing query """
    for part in query[1].split('and'):                                                      # Split on 'and' so you can do things like 'x' and ['y' or 'z'] ([] implied)
        adv_query = re.findall(r'(nick|hostmask|content|source) =~ \'(.+?)\'', part, re.I)  # Match sections of the query
        for match in adv_query:                                                             # For each 'or' section make a pass
        
            if first_pass:                                                                  # --- First pass (first 'and' part) will populate the matches list
                PAUSE_LOG = True                                                            #     Temporarily disable the logger, we don't want any concurrent mods
                for msg in messages:                                                        #     Iterate through all messages
                    if re.search(match[1], msg[match[0]]):                                  #     Check if the message matches the query's regex                                          
                        matches.append(msg)                                                 #     Add msg to matches list
                PAUSE_LOG = False                                                           #     Resume logging now that we are done iterating the log
                
            else:                                                                           # --- Do below on the second+ pass
                temp = []                                                                   #     Initialize empty list which will store this iteration's results
                for msg in matches:                                                         #     Iterate through every message found so far
                    if re.search(match[1], msg[match[0]]):                                  #     Check if it matches query
                        temp.append(msg)                                                    #     Append to the temp list
                matches = temp                                                              #     Set the old list to the temp
        
        first_pass = False                                                                  # It is now the second+ pass
    """ Done parsing query """
    
    if len(matches) == 0:                                                                   # No results, let the user know
        bot.say('[logquery] No results')
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
    if not PAUSE_LOG:
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
