# coding=utf-8
"""
deadfish.py - The fish are dead
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands
import sys
if sys.version_info.major < 3:
    str = unicode
    chr = unichr


@commands('df', 'deadfish')
def deadfish(bot, trigger):
    if not trigger.group(2):
        return bot.say('[Deadfish] \'i\' increments, \'d\' decrements, \'o\' outputs, \'s\' squares, \'r\' resets. Prefix with -s to convert outputs to char representations.')

    inp = trigger.group(2)

    memory = 0

    charoutput = False
    if trigger.group(3).startswith('-'):
        args = trigger.group(3)[1:]
        if 's' in args:
            charoutput = True
        inp = trigger.group(2).lstrip(trigger.group(3)).strip()

    output = []
    for c in inp:
        if memory == 256 or memory < 0 or memory > 9223372036859223372036854775807:  # Synthetic max limit
            memory = 0  # Overflow
        if c == 'i':
            memory += 1  # Increment
        if c == 'd':
            memory -= 1  # Decrement
        if c == 'r':
            memory = 0  # Inline reset (very handy)
        if c == 'o':
            output.append(memory)  # Output
        if c == 's':
            memory *= memory  # Square

    outputstr = ' '.join(str(x) for x in output)
    if charoutput:
        outputstr = ''
        for rep in output:
            outputstr += chr(rep)

    bot.say(outputstr)
