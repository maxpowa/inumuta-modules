# coding=utf-8
"""
dice.py - Dice Module
Copyright 2010-2013, Dimitri "Tyrope" Molenaars, TyRope.nl
Copyright 2013, Ari Koivula, <ari@koivu.la>
Copyright 2015, Max Gurela <maxpowa@outlook.com>
Licensed under the Eiffel Forum License 2.

http://sopel.chat/
"""
from __future__ import unicode_literals, absolute_import, print_function, division
import random
import re
import sys

import sopel.module
from sopel.tools.calculation import eval_equation
if sys.version_info.major < 3:
    int = long


@sopel.module.commands("roll")
@sopel.module.commands("dice")
@sopel.module.commands("d")
@sopel.module.priority("medium")
@sopel.module.example(".roll 3d1+1", 'You roll 3d1+1: (1+1+1)+1 = 4')
@sopel.module.example(".roll 2d4", 'You roll 2d4: \(\d\+\d\) = \d', re=True)
@sopel.module.example(".roll 100d1", '[^:]*: \(100\*1\) = 100', re=True)
@sopel.module.example(".roll 1001d1", 'Sorry, I only have 1000 dice.')
@sopel.module.example(".roll 1d1 + 1d1", 'You roll 1d1 + 1d1: (1)+(1) = 2')
@sopel.module.example(".roll 1d1+1d1", 'You roll 1d1+1d1: (1)+(1) = 2')
def roll(bot, trigger):
    """.dice XdY[vZ][+N], rolls dice and reports the result.

    X is the number of dice. Y is the number of faces in the dice. Z is the
    number of lowest dice to be dropped from the result. N is the constant to
    be applied to the end result.
    """

    def num(s):
        try:
            return int(s)
        except ValueError:
            return float(s)

    def term(t):
        parts = t.split('*')
        val = 1
        rolls = []
        for die in parts:
            res, roll = factor(die)
            if res == None:
                return None, roll
            val *= res
            rolls.append(roll)
        return val, '*'.join(rolls)

    def pretty_print(arr, dice):
        s = []
        for val in set(arr):
            count = arr.count(val)
            if count > 1 and dice > 10:
                s.append('%d*%d' % (count, val))
                continue
            for y in range(count):
                s.append('%d' % (val,))
        if len(s) > 0 and len(s) <= 10:
            s = '+'.join(s)
        elif dice <= 0:
            s = ''
        else:
            s = '...'
        return s

    def factor(f):
        g = f.split('d')
        if len(g)==1:
            try:
                return num(f), f
            except ValueError:
                return None, (f + ' is not a valid number')

        drop = 0
        if 'v' in g[1]:
            split = g[1].split('v')
            g[1] = split[0]
            try:
                drop = num(split[1]) if split[1] else 1
            except ValueError:
                return None, (str(split[1]) + ' is not a valid number of die to drop')
            if type(drop) is float:
                return None, 'You cannot drop a floating point number of die.'
            elif drop < 0:
                return None, 'You cannot drop a negative number of die.'

        try:
            g[0] = num(g[0]) if g[0] else 1
        except ValueError:
            return None, (str(g[0]) + ' is not a valid die count')
        negative = False
        if type(g[0]) is float:
            return None, 'You cannot roll a floating point number of die.'
        elif g[0] > 1000:
            return None, 'Sorry, I only have 1000 dice.'
        elif g[0] < drop:
            return None, 'You cannot drop more die than you roll.'
        elif g[0] < 0:
            negative = True
            g[0] = int(abs(g[0]))

        try:
            g[1] = num(g[1]) if g[1] else 6
        except ValueError:
            return None, (str(g[1]) + ' is not a valid number of die sides')
        if type(g[1]) is float:
            return None, 'I don\'t have any floating point die, sorry.'
        elif g[1] < 0:
            return None, "I don't have any die with a negative number of sides."

        rolls = []
        for i in range(g[0]):
            rolls.append(random.randint(1, g[1]))

        rolls = sorted(rolls, reverse=True)

        # Collect the die we dropped from the result
        dropped = []
        if drop > 0:
            dropped = rolls[len(rolls) - drop:]
            rolls =  rolls[:len(rolls) - drop]

        s = pretty_print(rolls, g[0] - drop)
        if drop > 0:
            s = s + '[+' + pretty_print(dropped, drop) + ']'
        total = sum(rolls)
        if negative:
            total = total * -1
        return total, '%s(%s)' % ('-' if negative else '', s)

    orig_str = trigger.group(2).lower()
    parts = []
    parts_s = []
    for piece in orig_str.split('+'):
        p, s = term(piece)
        if p == None:
            return bot.reply(s)
        parts.append(p)
        parts_s.append(s)
    result = sum(parts)

    bot.reply("You roll %s: %s = %d" % (orig_str, '+'.join(parts_s), result))


@sopel.module.commands("choice")
@sopel.module.commands("ch")
@sopel.module.commands("choose")
@sopel.module.priority("medium")
def choose(bot, trigger):
    """
    .choice option1|option2|option3 - Makes a difficult choice easy.
    """
    if not trigger.group(2):
        return bot.reply('I\'d choose an option, but you didn\'t give me any.')
    choices = re.split('[\|\\\\\/]', trigger.group(2))
    pick = random.choice(choices)
    return bot.reply('Your options: %s. My choice: %s' % (', '.join(choices), pick))


if __name__ == "__main__":
    from sopel.test_tools import run_example_tests
    run_example_tests(__file__)
