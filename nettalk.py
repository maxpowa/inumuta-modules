# coding=utf8
"""
nettalk.py - Sopel Nettalk Decrypter
Copyright 2015, Max Gurela <maxpowa@outlook.com>
Licensed under the Eiffel Forum License 2.

Adapted from https://github.com/grawity/code/blob/2ac8eadebeb113f25093f4542c16dad81f5eb5b1/security/denettalk
"""
from __future__ import unicode_literals

from sopel.module import rule, example
import sys, re
if sys.version_info.major >= 3:
    xrange = range
else:
    chr = unichr

codeChr = "0123456789abcdefghijklmnopqrstuvwxyz!?#%-+"
multPl = 71

def decrypt(key, msg):
    def go(i, lastCVal, rest):
        if len(rest) < 2:
            return ""
        c1, c2, rest = list(rest[:2]) + [rest[2:]]
        i1 = codeChr.find(c1)
        i2 = codeChr.find(c2)
        charVal = (i2 * 42 + i1 - key + multPl * i - lastCVal * (13 + i * 7)) % 1764
        return chr(charVal % 128) + go(i+1, i2+1, rest)
    return go(1, 0, msg[10:])

def try_all_keys(enc):
    for key in xrange(1764):
        msg = decrypt(key, enc)
        if msg.endswith("<>"):
            yield msg[:-2]

def bruteforce(enc):
    from collections import defaultdict

    # sometimes up to 10 different keys may work - most of them will decrypt to
    # the correct plaintext, others will decrypt ~80% correctly but have
    # garbage in some places; so try all keys but return only the version that
    # occurs most often.

    variants = defaultdict(int)
    for msg in try_all_keys(enc):
        variants[msg] += 1

    variants = list(variants.items())
    variants.sort(key=lambda x: x[1])

    yield variants[-1][0]

def escape(s):
    return repr(s)[1:-1]

@rule('\[NTCTC001\|(.+?)\]')
@example('[NTCTC001|9j9if?wvtz]', '<.+?> nop', re=True)
def decrypt_nettalk(bot, trigger):
    for msg in bruteforce(trigger.group(0)):
        bot.say('<{}> {}'.format(trigger.nick, msg))
