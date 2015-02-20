# coding=utf8
"""
deadfish.py - The fish are dead
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands

@commands('df','deadfish')
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
        if memory == 256 or memory < 0:
            memory = 0 #Overflow
        if c == u'i':
            memory += 1 #Increment
        if c == u'd':
            memory -= 1 #Decrement
        if c == u'r':
            memory = 0 # Inline reset (very handy)
        if c == u'o':
            output.append(memory) #Output
        if c == u's':
            memory *= memory #Square

    outputstr = u' '.join(str(x) for x in output)
    if charoutput:
        outputstr = u''
        for rep in output:
            outputstr += unichr(rep)

    bot.say(outputstr)
