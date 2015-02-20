"""
fun.py - Just a collection of random commands
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie import module, web
from willie.formatting import color
import json
import os
import string
import random
import re
from random import randint, choice


@module.commands('encode')
def encode(bot, trigger):
    encoding = trigger.group(3)
    text = trigger.group(2)
    if not encoding or not text:
        bot.say('encode usage: .encode <encoding> <string>')
        return

    text = text.replace(encoding, '', 1).strip()

    if (encoding.lower() == 'binary'):
        bot.say(''.join('{:08b}'.format(ord(c)) for c in text))
        return
    try:
        bot.say(text.encode(encoding, 'strict'))
    except Exception as e:
        bot.say('[Encode] {}'.format(e.message))


@module.commands('decode')
def decode(bot, trigger):
    encoding = trigger.group(3)
    text = trigger.group(2)
    if not encoding or not text:
        bot.say('decode usage: .decode <encoding> <string>')
        return

    text = text.replace(encoding, '', 1).strip()

    if (encoding.lower() == 'binary'):
        if (set(text) == set([u'1', u'0'])):
            bot.say(''.join(chr(int(text[i:i + 8], 2)) for i in xrange(0, len(text), 8)))
            return
        else:
            bot.say('[Decode] Invalid binary string')
    try:
        bot.say(text.decode(encoding, 'strict'))
    except Exception as e:
        bot.say('[Decode] {}'.format(e.message))


@module.commands('rainbow')
def rainbow(bot, trigger):
    text = trigger.group(2)
    if not text:
        text = 'rainbow'
    num = 2
    out = ''
    for c in text:
        out += color(c, num)
        if num < 15:
            num += 1
        else:
            num = 2
    bot.say(out)


@module.rule(' ?\*?\/?shrug\*?')
def shrug(bot, trigger):
    bot.say(u'\u00AF\_(\u30C4)_/\u00AF')


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
        bot.say(u'(\u2229 \u0361\u00B0 \u035C\u0296 \u0361\u00B0)\u2283\u2501\u2606\uFF9F. * \uFF65 \uFF61\uFF9F, * ' + trigger.group(2).strip())
    else:
        bot.say(u'(\u2229 \u0361\u00B0 \u035C\u0296 \u0361\u00B0)\u2283\u2501\u2606\uFF9F. * \uFF65 \uFF61\uFF9F, *')


@module.commands('spoiler')
def reverse(bot, trigger):
    """
    .spoiler <where> <text> - Create a 'spoiler' that can be read by selecting the text
    """
    if trigger.group(3):
        bot.msg(trigger.group(3), u'\u202E\u202E' + trigger.group(2).replace(trigger.group(3), '').strip())
    else:
        bot.say('Usage: .spoiler <where> <text>')


@module.commands('kernel')
def kernel(bot, trigger):
    """
    .kernel - Show the latest linux kernels
    """
    contents = web.get("https://www.kernel.org/finger_banner")
    contents = re.sub(r'The latest(\s*)', '', contents)
    contents = re.sub(r'version of the Linux kernel is:(\s*)', '- ', contents)
    lines = contents.split("\n")

    message = "Linux kernel versions: "
    message += ", ".join(line for line in lines[:-1])
    bot.say(message)


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
        bot.say(u'\u10DA(\u0301\u25C9\u25DE\u0C6A\u25DF\u25C9\u2035\u10DA) let me hold your ' + trigger.group(2).strip().lower() + u' for a while \u10DA(\u0301\u25C9\u25DE\u0C6A\u25DF\u25C9\u2035\u10DA)')
    else:
        bot.say(u'\u10DA(\u0301\u25C9\u25DE\u0C6A\u25DF\u25C9\u2035\u10DA) let me hold your donger for a while \u10DA(\u0301\u25C9\u25DE\u0C6A\u25DF\u25C9\u2035\u10DA)')


@module.commands('unseen')
def unseen(bot, trigger):
    """
    .unseen [donger] - The unseen donger
    """
    if trigger.group(2):
        bot.say(u'(\u0E07\u0360\u00B0\u035F\u0644\u035C\u0361\u00B0)\u0E07 \u1D1B\u029C\u1D07 \u1D1C\u0274s\u1D07\u1D07\u0274 {} \u026As \u1D1B\u029C\u1D07 \u1D05\u1D07\u1D00\u1D05\u029F\u026A\u1D07s\u1D1B (\u0E07\u0360\u00B0\u035F\u0644\u035C\u0361\u00B0)\u0E07'.format(smallcaps(trigger.group(2).strip())))
    else:
        bot.say(u'(\u0E07\u0360\u00B0\u035F\u0644\u035C\u0361\u00B0)\u0E07 \u1D1B\u029C\u1D07 \u1D1C\u0274s\u1D07\u1D07\u0274 \u1D05\u1D0F\u0274\u0262\u1D07\u0280 \u026As \u1D1B\u029C\u1D07 \u1D05\u1D07\u1D00\u1D05\u029F\u026A\u1D07s\u1D1B (\u0E07\u0360\u00B0\u035F\u0644\u035C\u0361\u00B0)\u0E07')


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
        bot.say(u'\u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89 raise your {} \u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89'.format(trigger.group(2).strip().lower()))
    else:
        bot.say(u'\u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89 raise your dongers \u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89')


@module.commands('fight')
def fight_me(bot, trigger):
    """
    .fight [person] - Just fight em
    """
    if trigger.group(2):
        bot.say(u'(\u0E07\'\u0300-\'\u0301)\u0E07 FIGHT ME {} (\u0E07\'\u0300-\'\u0301)\u0E07'.format(trigger.group(2).strip().upper()))
    else:
        bot.say(u'(\u0E07\'\u0300-\'\u0301)\u0E07 FIGHT ME {} (\u0E07\'\u0300-\'\u0301)\u0E07'.format(trigger.nick.upper()))


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


@module.rule(u'.*(\(\u256F\u00B0\u25A1\u00B0\)\u256F\uFE35 \u253B\u2501\u253B|\(\u256F\u00B0\u25A1\u00B0\uFF09\u256F\uFE35 \u253B\u2501\u253B|\(\u30CE\u0CA0\u76CA\u0CA0\)\u30CE\u5F61\u253B\u2501\u253B|\u253B\u2501\u253B).*')
def table_upright(bot, trigger):
    uprights = [u'\u252C\u2500\u252C \u30CE(^_^\u30CE)', u'\u252C\u2500\u252C\u30CE(\u00BA_\u00BA\u30CE)']
    bot.say(random.choice(uprights))


@module.commands('riot')
def riot(bot, trigger):
    """
    .riot [text] - X OR RIOT
    """
    if trigger.group(2):
        bot.say(u'\u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89 {} OR RIOT \u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89'.format(trigger.group(2).strip().upper()))
    else:
        bot.say(u'\u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89 RIOT \u30FD\u0F3C\u0E88\u0644\u035C\u0E88\u0F3D\uFF89')


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
    bot.say(flip_text(trigger.group(2).strip()))

#
# TEXT SWIRL-IFIER
#

def swirl_text(text):
    if not text:
        return None
    else:
        swirl_chars = [u'\u0E04', u'\u0E52', u'\u03C2', u'\u0E54', u'\u0454', u'\u0166', u'\uFEEE', u'\u0452', u'\u0E40', u'\u05DF', u'\u043A', u'l', u'\u0E53', u'\u0E20', u'\u0E4F', u'\u05E7', u'\u1EE3', u'\u0433', u'\u0E23', u't', u'\u0E22', u'\u05E9', u'\u0E2C', u'\u05D0', u'\u05E5', u'z']
        abc_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        comb_map = dict(zip(abc_chars, swirl_chars))
        #return str(comb_map)
        return replace_all(text.lower(), comb_map)

#
# TEXT FLIPPER
#

def flip_text(text):
    if not text:
        return None
    else:
        flip_chars = [u'\u0250', u'q', u'\u0254', u'p', u'\u01DD', u'\u025F', u'\u0183', u'\u0265', u'\u0131', u'\u027E', u'\u029E', u'l', u'\u026F', u'u', u'o', u'd', u'b', u'\u0279', u's', u'\u0287', u'n', u'\u028C', u'\u028D', u'x', u'\u028E', u'z', r'\\', r'/']
        abc_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', r'/', r'\\']
        comb_map = dict(zip(abc_chars, flip_chars))
        #return str(comb_map)
        return replace_all(text.lower()[::-1], comb_map)
#
# ZALGO CONVERTER
#

unoise = u''.join(map(unichr, xrange(0x300, 0x36F)))


def mungle(char, intensity=10):
    return char + u''.join(random.sample(unoise, intensity))

#
# SMALLCAPS CONVERTER
#

def smallcaps(text):
    if not text:
        return None
    else:
        sc_chars = [u'\u1D00', u'\u0299', u'\u1D04', u'\u1D05', u'\u1D07', u'\u0493', u'\u0262', u'\u029C', u'\u026A', u'\u1D0A', u'\u1D0B', u'\u029F', u'\u1D0D', u'\u0274', u'\u1D0F', u'\u1D18', u'\u01EB', u'\u0280', u's', u'\u1D1B', u'\u1D1C', u'\u1D20', u'\u1D21', u'x', u'\u028F', u'\u1D22']
        abc_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        comb_map = dict(zip(abc_chars, sc_chars))
        #return comb_map
        return replace_all(text.lower(), comb_map)


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
