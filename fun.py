# coding=utf-8
"""
fun.py - Just a collection of random commands
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel import module, web
from sopel.formatting import color
import json
import os
import string
import random
import re
import sys
from random import randint, choice
if sys.version_info.major >= 3:
    xrange = range
else:
    chr = unichr

def rotate(l, n):
    return l[n:] + l[:n]


@module.rate(10)
@module.rule('^neat$')
def neat(bot, trigger):
    bot.say('https://i.imgur.com/8GfHgHe.jpg')


@module.rate(10)
@module.rule('.*(?:l-)?lewd.*')
def lewd(bot, trigger):
    messages = ['https://i.imgur.com/reAqk3e.png', 'http://i.imgur.com/I3apoUB.gif', 'http://i.imgur.com/um5vVcC.gif', 'http://i.imgur.com/pTb7vbZ.gif', 'http://i.imgur.com/cqiyR1L.gif', 'http://i.imgur.com/vZnMTFn.gif', 'http://i.imgur.com/Ftuig9v.gif', 'http://i.imgur.com/Gygj9sg.gif', 'http://i.imgur.com/pPVVu2b.gif', 'http://i.imgur.com/7QCizTa.gif', 'http://i.imgur.com/PS12w7X.gif', 'http://i.imgur.com/eBjiGR9.gif', 'http://i.imgur.com/7ncmr6H.png']
    bot.say("Lewd! " + random.choice(messages))


@module.commands('rainbow')
def rainbow(bot, trigger):
    text = trigger.group(2)
    if not text:
        text = 'rainbow'
    rainbow = [4, 7, 8, 3, 12, 2, 6]
    out = ''
    for c in text:
        out += color(c, rainbow[0])
        rainbow = rotate(rainbow, 1)
    bot.say(out)


@module.commands('grill')
def grill(bot, trigger):
    bot.say('http://i.imgur.com/YYZmtbs.png')


@module.rule(' ?\*?\/?shrug\*?')
def shrug(bot, trigger):
    bot.say('\u00AF\_(\u30C4)_/\u00AF')


@module.commands('insult')
def insult(bot, trigger):
    """
    .insult [target]
    """
    raw = web.get('http://quandyfactory.com/insult/json')
    insults = json.loads(raw)
    if trigger.group(3):
        bot.say(trigger.group(3) + ', ' + insults['insult'])
    else:
        bot.say(trigger.nick + ', ' + insults['insult'])


@module.commands('magic')
def magic(bot, trigger):
    """
    .magic [target] - Cast your magic wand!
    """
    if trigger.group(2):
        bot.say('(\u2229 \u0361\u00B0 \u035C\u0296 \u0361\u00B0)\u2283\u2501\u2606\uFF9F. * \uFF65 \uFF61\uFF9F, * ' + trigger.group(2).strip())
    else:
        bot.say('(\u2229 \u0361\u00B0 \u035C\u0296 \u0361\u00B0)\u2283\u2501\u2606\uFF9F. * \uFF65 \uFF61\uFF9F, *')


@module.commands('spoiler')
def reverse(bot, trigger):
    """
    .spoiler <where> <text> - Create a 'spoiler' that can be read by selecting the text
    """
    if trigger.group(3):
        bot.msg(trigger.group(3), '\u202E\u202E' + trigger.group(2).replace(trigger.group(3), '').strip())
    else:
        bot.say('Usage: .spoiler <where> <text>')


@module.commands('rimshot')
def rimshot(bot, trigger):
    """
    .rimshot - Badum-tiss
    """
    bot.say('*Badumtsss*')


@module.commands('uwot')
def uwot(bot, trigger):
    """
    .uwot [target] - http://vazkii.us/uwot.ogg
    """
    if trigger.group(2):
        bot.say(trigger.group(2).strip() + ': http://vazkii.us/uwot.ogg')
    else:
        bot.reply('http://vazkii.us/uwot.ogg')


@module.commands('swirl')
def swirl(bot, trigger):
    """
    .swirl [text] - Make text swirly!
    """
    if trigger.group(2):
        bot.say(swirl_text(trigger.group(2).strip()))
    else:
        bot.say(swirl_text('swirly text'))


@module.commands('hold')
def hold(bot, trigger):
    """
    .hold [target] - I'll hold it forever!
    """
    if trigger.group(2):
        bot.say('\u10DA(\u0301\u25C9\u25DE\u0C6A\u25DF\u25C9\u2035\u10DA) let me hold your ' + trigger.group(2).strip().lower() + ' for a while \u10DA(\u0301\u25C9\u25DE\u0C6A\u25DF\u25C9\u2035\u10DA)')
    else:
        bot.say('\u10DA(\u0301\u25C9\u25DE\u0C6A\u25DF\u25C9\u2035\u10DA) let me hold your donger for a while \u10DA(\u0301\u25C9\u25DE\u0C6A\u25DF\u25C9\u2035\u10DA)')


@module.commands('unseen')
def unseen(bot, trigger):
    """
    .unseen [donger] - The unseen donger
    """
    if trigger.group(2):
        bot.say('(\u0E07\u0360\u00B0\u035F\u0644\u035C\u0361\u00B0)\u0E07 \u1D1B\u029C\u1D07 \u1D1C\u0274s\u1D07\u1D07\u0274 {} \u026As \u1D1B\u029C\u1D07 \u1D05\u1D07\u1D00\u1D05\u029F\u026A\u1D07s\u1D1B (\u0E07\u0360\u00B0\u035F\u0644\u035C\u0361\u00B0)\u0E07'.format(smallcaps(trigger.group(2).strip())))
    else:
        bot.say('(\u0E07\u0360\u00B0\u035F\u0644\u035C\u0361\u00B0)\u0E07 \u1D1B\u029C\u1D07 \u1D1C\u0274s\u1D07\u1D07\u0274 \u1D05\u1D0F\u0274\u0262\u1D07\u0280 \u026As \u1D1B\u029C\u1D07 \u1D05\u1D07\u1D00\u1D05\u029F\u026A\u1D07s\u1D1B (\u0E07\u0360\u00B0\u035F\u0644\u035C\u0361\u00B0)\u0E07')


@module.commands('smallcaps')
def sc_convert(bot, trigger):
    """
    .smallcaps [text] - Convert text to smallcaps text
    """
    if trigger.group(2):
        bot.say(smallcaps(trigger.group(2).strip()))
    else:
        bot.say('Give me a message to turn into ' + smallcaps('smallcaps'))


@module.commands('raise')
def raise_dongers(bot, trigger):
    """
    .raise [dongers] - Raise those dongers.
    """
    if trigger.group(2):
        bot.say('\u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89 raise your {} \u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89'.format(trigger.group(2).strip().lower()))
    else:
        bot.say('\u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89 raise your dongers \u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89')


@module.commands('praise')
def praise_the_sun(bot, trigger):
    """
    .praise [the sun] - \[T]/
    """
    if trigger.group(2):
        bot.say('\[T]/ \[T]/ PRAISE {}! \[T]/ \[T]/'.format(trigger.group(2).strip().upper()))
    else:
        bot.say('\[T]/ \[T]/ PRAISE THE SUN! \[T]/ \[T]/')


@module.commands('fight')
def fight_me(bot, trigger):
    """
    .fight [person] - Just fight em
    """
    if trigger.group(2):
        bot.say('(\u0E07\'\u0300-\'\u0301)\u0E07 FIGHT ME {} (\u0E07\'\u0300-\'\u0301)\u0E07'.format(trigger.group(2).strip().upper()))
    else:
        bot.say('(\u0E07\'\u0300-\'\u0301)\u0E07 FIGHT ME {} (\u0E07\'\u0300-\'\u0301)\u0E07'.format(trigger.nick.upper()))


@module.commands('hail')
def hail_hydra(bot, trigger):
    """
    .hail [party] - Hails party of choice, will hail hydra if no direction is given.
    """
    if trigger.group(2):
        bot.say('/o/ /o/ HAIL ' + trigger.group(2).upper() + ' \\o\\ \\o\\')
    else:
        bot.say('HAIL HYDRA')


@module.commands('salute')
def salute(bot, trigger):
    """
    .salute <party> - Salutes party of choice, will not do anything unless given party to salute
    """
    if trigger.group(2):
        bot.say('o7 o7 SALUTE ' + trigger.group(2).upper() + ' o7 o7')


@module.commands('rollover')
def rollover(bot, trigger):
    """
    .rollover - Hey boy! Roll over! ... Good boy!
    """
    bot.say('(._.) (|:) (.-.) (:|) (._.)')


@module.rule('.*(\(\u256F\u00B0\u25A1\u00B0\)\u256F\uFE35 \u253B\u2501\u253B|\(\u256F\u00B0\u25A1\u00B0\uFF09\u256F\uFE35 \u253B\u2501\u253B|\(\u30CE\u0CA0\u76CA\u0CA0\)\u30CE\u5F61\u253B\u2501\u253B|\u253B\u2501\u253B).*')
def table_upright(bot, trigger):
    uprights = ['\u252C\u2500\u252C \u30CE(^_^\u30CE)', '\u252C\u2500\u252C\u30CE(\u00BA_\u00BA\u30CE)']
    bot.say(random.choice(uprights))


@module.commands('riot')
def riot(bot, trigger):
    """
    .riot [text] - X OR RIOT
    """
    if trigger.group(2):
        bot.say('\u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89 {} OR RIOT \u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89'.format(trigger.group(2).strip().upper()))
    else:
        bot.say('\u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89 RIOT \u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89')


@module.commands('zalgo')
def zalgo_cmd(bot, trigger):
    """
    .zalgo [text] - Zalgo-izes text. Will zalgo the word 'zalgo' if no text is given.
    """
    text = ''.join(map(mungle, 'zalgo'.decode('utf8'))).encode('utf8')
    if trigger.group(2):
        try:
            text = ''.join(map(mungle, trigger.group(2).decode('utf8'))).encode('utf8', 'ignore')
        except UnicodeEncodeError:
            text = ''.join(map(mungle, trigger.group(2).encode('ascii', 'ignore'))).encode('utf8', 'ignore')

    #This is a hacky fix, but it works. See https://gist.github.com/grawity/3257896 for why it's needed
    remainder = 496 - len(bot.nick + bot.user + 'irc.everythingisawesome.us' + trigger.sender)
    if len(text) > remainder:
        text = text[:remainder]

    bot.say(text)


@module.commands('flip')
def flip(bot, trigger):
    """
    .flip [text] - Flips text upside down
    """
    if (trigger.group(2)):
        bot.say('(\u256f\u00b0\u25a1\u00b0\uff09\u256f\ufe35 ' + flip_text(trigger.group(2).strip()))
    else:
        bot.say('(\u256f\u00b0\u25a1\u00b0\uff09\u256f\ufe35 \u253B\u2501\u253B')

# TEXT SWIRL-IFIER
def swirl_text(text):
    if not text:
        return None
    else:
        swirl_chars = ['\u0E04', '\u0E52', '\u03C2', '\u0E54', '\u0454', '\u0166', '\uFEEE', '\u0452', '\u0E40', '\u05DF', '\u043A', 'l', '\u0E53', '\u0E20', '\u0E4F', '\u05E7', '\u1EE3', '\u0433', '\u0E23', 't', '\u0E22', '\u05E9', '\u0E2C', '\u05D0', '\u05E5', 'z']
        abc_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        comb_map = dict(zip(abc_chars, swirl_chars))
        #return str(comb_map)
        return replace_all(text.lower(), comb_map)


# TEXT FLIPPER
def flip_text(text):
    if not text:
        return None
    else:
        flip_chars = ['\u0250', 'q', '\u0254', 'p', '\u01DD', '\u025F', '\u0183', '\u0265', '\u0131', '\u027E', '\u029E', 'l', '\u026F', 'u', 'o', 'd', 'b', '\u0279', 's', '\u0287', 'n', '\u028C', '\u028D', 'x', '\u028E', 'z', r'\\', r'/']
        abc_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', r'/', r'\\']
        comb_map = dict(zip(abc_chars, flip_chars))
        #return str(comb_map)
        return replace_all(text.lower()[::-1], comb_map)
#
# ZALGO CONVERTER
#

unoise = ''.join(map(chr, xrange(0x300, 0x36F)))


def mungle(char, intensity=10):
    return char + ''.join(random.sample(unoise, intensity))


# SMALLCAPS CONVERTER
def smallcaps(text):
    if not text:
        return None
    else:
        sc_chars = ['\u1D00', '\u0299', '\u1D04', '\u1D05', '\u1D07', '\u0493', '\u0262', '\u029C', '\u026A', '\u1D0A', '\u1D0B', '\u029F', '\u1D0D', '\u0274', '\u1D0F', '\u1D18', '\u01EB', '\u0280', 's', '\u1D1B', '\u1D1C', '\u1D20', '\u1D21', 'x', '\u028F', '\u1D22']
        abc_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        comb_map = dict(zip(abc_chars, sc_chars))
        #return comb_map
        return replace_all(text.lower(), comb_map)


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
