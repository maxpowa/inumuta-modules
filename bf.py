# coding=utf8
"""
bf.py - brainfuck interpreter adapted from
https://github.com/infinitylabs/uguubot/blob/master/disabled_plugins/bf.py
and
https://github.com/yiangos/python-text-to-brainfuck/blob/master/BFGenerator.py

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import commands, thread
from io import StringIO as StringIO
import re
import random

BUFFER_SIZE = 5000
MAX_STEPS = 1000000


@thread(True)
@commands('brainfuck', 'bf')
def brainfuck(bot, trigger):
    try:
        if trigger.group(2):
            bot.say(bf(trigger.group(2)))
        else:
            bot.say(bf('++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.'))
    except:
        bot.say('Way to go, you broke it. I hope you\'re happy.')


@thread(True)
@commands('fuckbrain', 'fb')
def fuckbrain(bot, trigger):
    try:
        if trigger.group(2):
            resp = fb(trigger.group(2))
            if len(resp) > 440:
                bot.say('Sorry, the response was too long.')
                return
            bot.say(resp)
        else:
            bot.say(fb('Hello World!'))
    except:
        bot.say('Way to go, you broke it. I hope you\'re happy.')


def fb(inp):
    bfg = BFGenerator()
    return bfg.text_to_brainfuck(inp)


def bf(inp):
    program = re.sub('[^][<>+-.,]', '', inp)

    # create a dict of brackets pairs, for speed later on
    brackets = {}
    open_brackets = []
    for pos in range(len(program)):
        if program[pos] == '[':
            open_brackets.append(pos)
        elif program[pos] == ']':
            if len(open_brackets) > 0:
                brackets[pos] = open_brackets[-1]
                brackets[open_brackets[-1]] = pos
                open_brackets.pop()
            else:
                return 'unbalanced brackets'
    if len(open_brackets) != 0:
        return 'unbalanced brackets'

    # now we can start interpreting
    ip = 0        # instruction pointer
    mp = 0        # memory pointer
    steps = 0
    memory = [0] * BUFFER_SIZE  # initial memory area
    rightmost = 0
    output = ""   # we'll save the output here

    # the main program loop:
    while ip < len(program):
        c = program[ip]
        if c == '+':
            memory[mp] = memory[mp] + 1 % 256
        elif c == '-':
            memory[mp] = memory[mp] - 1 % 256
        elif c == '>':
            mp += 1
            if mp > rightmost:
                rightmost = mp
                if mp >= len(memory):
                    # no restriction on memory growth!
                    memory.extend([0] * BUFFER_SIZE)
        elif c == '<':
            mp = mp - 1 % len(memory)
        elif c == '.':
            output += chr(memory[mp])
            if len(output) > 500:
                break
        elif c == ',':
            memory[mp] = random.randint(1, 255)
        elif c == '[':
            if memory[mp] == 0:
                ip = brackets[ip]
        elif c == ']':
            if memory[mp] != 0:
                ip = brackets[ip]

        ip += 1
        steps += 1
        if steps > MAX_STEPS:
            if output == '':
                output = '(no output)'
            output += '[exceeded %d iterations]' % MAX_STEPS
            break

    stripped_output = re.sub(r'[\x00-\x1F]', '', output)

    if stripped_output == '':
        if output != '':
            return 'no printable output'
        return 'no output'

    return stripped_output[:430].decode('utf8', 'ignore')


class BFGenerator(object):
    """Takes a string and generates a brainfuck code that, when run,
       prints the original string to the brainfuck interpreter standard
       output"""

    def text_to_brainfuck(self, data):
        """Converts a string into a BF program. Returns the BF code"""
        glyphs = len(set([c for c in data]))
        number_of_bins = max(max([ord(c) for c in data]) // glyphs, 1)
        # Create an array that emulates the BF memory array as if the
        # code we are generating was being executed. Initialize the
        # array by creating as many elements as different glyphs in
        # the original string. Then each "bin" gets an initial value
        # which is determined by the actual message.
        # FIXME: I can see how this can become a problem for languages
        # that don't use a phonetic alphabet, such as Chinese.
        bins = [(i + 1) * number_of_bins for i in range(glyphs)]
        code = "+" * number_of_bins + "["
        code += "".join([">" + ("+" * (i + 1)) for i in range(1, glyphs)])
        code += "<" * (glyphs - 1) + "-]"
        code += "+" * number_of_bins
        # For each character in the original message, find the position
        # that holds the value closest to the character's ordinal, then
        # generate the BF code to move the memory pointer to that memory
        # position, get the value of that memory position to be equal
        # to the ordinal of the character and print it (i.e. print the
        # character).
        current_bin = 0
        for char in data:
            new_bin = [abs(ord(char) - b)
                     for b in bins].index(min([abs(ord(char) - b)
                                               for b in bins]))
            appending_character = ""
            if new_bin - current_bin > 0:
                appending_character = ">"
            else:
                appending_character = "<"
            code += appending_character * abs(new_bin - current_bin)
            if ord(char) - bins[new_bin] > 0:
                appending_character = "+"
            else:
                appending_character = "-"
            code += (appending_character * abs(ord(char) - bins[new_bin])) + "."
            current_bin = new_bin
            bins[new_bin] = ord(char)
        return code
