# coding=utf8
"""
tell.py - Willie Tell and Ask Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

import os
import time
import datetime
import willie.tools
import threading
import sys
from willie.tools import iterkeys
from willie.module import commands

maximum = 4

def load_notes(fn, lock):
    lock.acquire()
    try:
        result = {}
        f = open(fn)
        for line in f:
            line = line.strip()
            if sys.version_info.major < 3:
                line = line.decode('utf-8')
            if line:
                try:
                    tellee, msg = line.split('\t', 1)
                except ValueError:
                    continue  # @@ hmm
                result.setdefault(tellee, []).append(msg)
        f.close()
    finally:
        lock.release()
    return result


def dump_notes(fn, data, lock):
    lock.acquire()
    try:
        f = open(fn, 'w')
        for tellee in iterkeys(data):
            for remindon in data[tellee]:
                line = remindon
                try:
                    to_write = tellee + '\t' + line + '\n'
                    if sys.version_info.major < 3:
                        to_write = to_write.encode('utf-8')
                    f.write(to_write)
                except IOError:
                    break
        try:
            f.close()
        except IOError:
            pass
    finally:
        lock.release()
    return True


def setup(self):
    fn = self.nick + '-' + self.config.host + '.note.db'
    self.note_filename = os.path.join(self.config.dotdir, fn)
    if not os.path.exists(self.note_filename):
        try:
            f = open(self.note_filename, 'w')
        except OSError:
            pass
        else:
            f.write('')
            f.close()
    self.memory['note_lock'] = threading.Lock()
    self.memory['notes'] = load_notes(self.note_filename, self.memory['note_lock'])


@commands('note', 'notes')
def note(bot, trigger):
    """ Give someone a message the next time they're seen """
    teller = trigger.nick
    
    if not os.path.exists(bot.note_filename):
        bot.say('Notes database does not exist D:')
        return
        
    if not trigger.group(2):
        bot.say('Usage: .note <add|show|del> [arg] - Add personal notes. Will always be returned via notice [your secret is safe with me ;)]')
        return

    if trigger.group(3).lower() == 'add':
        bot.memory['note_lock'].acquire()
        try:
            if not teller in bot.memory['notes']:
                bot.memory['notes'][teller] = [trigger.group(2).lstrip(trigger.group(3)).strip()]
            else:
                bot.memory['notes'][teller].append(trigger.group(2).lstrip(trigger.group(3)).strip())
        finally:
            bot.memory['note_lock'].release()

        response = "Added to your notes. Total notes: %s" % str(len(bot.memory['notes'][teller]))

        bot.reply(response)
    elif trigger.group(3).lower() == 'show':
        show_notes(bot, teller)
    elif trigger.group(3).lower() == 'del':
        remove_note(bot, trigger)
        
    dump_notes(bot.note_filename, bot.memory['notes'], bot.memory['note_lock'])

def remove_note(bot, trigger):
    if trigger.group(4).isdigit():
        bot.notice("Removing note: %s" % bot.memory['notes'][trigger.nick][int(trigger.group(4))], recipient=trigger.nick)
        del bot.memory['notes'][trigger.nick][int(trigger.group(4))]
    else:
        bot.notice("Invalid index, please ensure that note index exists", recipient=trigger.nick)
    
def get_notes(bot, key):
    lines = []
    
    bot.memory['note_lock'].acquire()
    try:
        for msg in bot.memory['notes'][key]:
            lines.append(msg)
    finally:
        bot.memory['note_lock'].release()
    return lines
    
def show_notes(bot, user):
    notes = []
    remkeys = list(reversed(sorted(bot.memory['notes'].keys())))

    for remkey in remkeys:
        if not remkey.endswith('*') or remkey.endswith(':'):
            if user == remkey:
                notes.extend(get_notes(bot, remkey))
        elif user.startswith(remkey.rstrip('*:')):
            notes.extend(get_notes(bot, remkey))

    index = 0
    for line in notes:
        bot.notice("%s: %s" % (str(index), line), recipient=user)
        index += 1