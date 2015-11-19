# coding=utf-8
"""
dice.py - Dice Module
Copyright 2010-2013, Dimitri "Tyrope" Molenaars, TyRope.nl
Copyright 2013, Ari Koivula, <ari@koivu.la>
Licensed under the Eiffel Forum License 2.

http://sopel.chat/
"""
from __future__ import unicode_literals, absolute_import, print_function, division
import random
import re

import sopel.module
from sopel.tools.calculation import eval_equation


@sopel.module.commands("roll")
@sopel.module.commands("dice")
@sopel.module.commands("d")
@sopel.module.priority("medium")
@sopel.module.example(".roll 3d1+1", 'You roll 3d1+1: (1+1+1)+1 = 4')
@sopel.module.example(".roll 2d4", 'You roll 2d4: \(\d\+\d\) = \d', re=True)
@sopel.module.example(".roll 100d1", '[^:]*: \(100x1\) = 100', re=True)
@sopel.module.example(".roll 1001d1", 'Sorry, I only have 1000 dice.')
@sopel.module.example(".roll 1d1 + 1d1", 'You roll 1d1 + 1d1: (1) + (1) = 2')
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

    def factor(f):
        g = f.split('d')
        if len(g)==1:
            try:
                return num(f), f
            except ValueError:
                return None, (f + ' is not a valid number')

        try:
            g[0] = num(g[0]) if g[0] else 1
        except ValueError:
            return None, (str(g[0]) + ' is not a valid die count')
        if type(g[0]) is float:
            return None, 'You cannot roll a floating point number of die.'
        elif g[0] > 1000:
            return None, 'Sorry, I only have 1000 dice.'
        try:
            g[1] = num(g[1]) if g[1] else 6
        except ValueError:
            return None, (str(g[1]) + ' is not a valid number of die sides')
        if type(g[1]) is float:
            return None, 'I don\'t have any floating point die, sorry.'
        rolls = dict()
        rolls_s = []
        for i in range(g[0]):
            x = random.randint(1, g[1])
            rolls[x] = rolls.get(x, 0) + 1
        sorted(rolls, reverse=True)
        for x in rolls:
            if rolls[x] > 1 and g[0] > 10:
                rolls_s.append('%d*%d' % (rolls[x],x))
                continue
            for y in range(rolls[x]):
                rolls_s.append('%d' % (x,))
        if len(rolls_s) > 0 and len(rolls_s) <= 10:
            s = '+'.join(rolls_s)
        else:
            s = '...'
        return sum(val*rolls[val] for val in rolls), '(%s)' % s

    orig_str = trigger.group(2).lower()
    parts = []
    parts_s = []
    for piece in trigger.group(2).lower().split('+'):
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
