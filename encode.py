# coding=utf-8
"""
encode.py - Playing with encodings is fun, right?
Copyright 2015 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals

from sopel import module
from codecs import encode as _encode
from codecs import decode as _decode

import sys
if sys.version_info.major < 3:
    chr = unichr
    str = unicode

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
        bot.say(_encode(text, encoding, 'strict'))
    except (LookupError,UnicodeEncodeError) as e:
        bot.say('[encode] {}'.format(str(e)))


@module.commands('decode')
def decode(bot, trigger):
    encoding = trigger.group(3)
    text = trigger.group(2)
    if not encoding or not text:
        bot.say('decode usage: .decode <encoding> <string>')
        return

    text = text.replace(encoding, '', 1).strip()

    if (encoding.lower() == 'binary'):
        if (set(text) == set(['1', '0'])):
            bot.say(''.join(chr(int(text[i:i + 8], 2)) for i in xrange(0, len(text), 8)))
            return
        else:
            bot.say('[decode] Invalid binary string')
    try:
        bot.say(_decode(text, encoding, 'strict'))
    except (LookupError, UnicodeDecodeError) as e:
        bot.say('[decode] {}'.format(str(e)))
