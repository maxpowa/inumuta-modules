# coding=utf8
"""
nickometer.py - We already know how lame your nick is, here's proof
Copyright 2014 Max Gurela

Adapted from supybot https://github.com/Elwell/supybot/blob/master/plugins/Nickometer/plugin.py

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands
import re
import math
import string


def slowExponent(x):
    return 1.3 * x * (1 - math.atan(x / 6.0) * 2 / math.pi)


def slowPow(x, y):
    return math.pow(x, slowExponent(y))


def caseShifts(s):
    s = re.sub('[^a-zA-Z]', '', s)
    s = re.sub('[A-Z]+', 'U', s)
    s = re.sub('[a-z]+', 'l', s)
    return len(s) - 1


def numberShifts(s):
    s = re.sub('[^a-zA-Z0-9]', '', s)
    s = re.sub('[a-zA-Z]+', 'l', s)
    s = re.sub('[0-9]+', 'n', s)
    return len(s) - 1


def trans(to_translate, tabin, tabout):
    tabin = [ord(char) for char in tabin]
    translate_table = dict(zip(tabin, tabout))
    return to_translate.translate(translate_table)


@commands('nickometer')
def nickometer(bot, trigger):
    """
    .nickometer [nick] - Rate how lame a nick is using proprietary algorithms
    """
    score = 0
    nick = trigger.group(2)
    if not nick:
        nick = trigger.nick
    nick = nick.strip()
    originalNick = nick

    specialCost = [('69', 500),
                   ('dea?th', 500),
                   ('dark', 400),
                   ('n[i1]ght', 300),
                   ('n[i1]te', 500),
                   ('fuck', 500),
                   ('sh[i1]t', 500),
                   ('coo[l1]', 500),
                   ('kew[l1]', 500),
                   ('teh', 100),
                   ('lame', 500),
                   ('dood', 500),
                   ('dude', 500),
                   ('[l1](oo?|u)[sz]er', 500),
                   ('[l1]eet', 500),
                   ('e[l1]ite', 500),
                   ('[l1]ord', 500),
                   ('pron', 1000),
                   ('warez', 1000),
                   ('xx', 100),
                   ('\\[rkx]0', 1000),
                   ('\\0[rkx]', 1000)]

    for special in specialCost:
        tempNick = nick
        if special[0][0] != '\\':
            tempNick = trans(tempNick, u'023457+8', u'ozeasttb')

        if tempNick and re.search(special[0], tempNick, re.IGNORECASE):
            score += special[1]

    # Allow Perl referencing
    nick = re.sub('^\\\\([A-Za-z])', '\1', nick)

    # Punish consecutive non-alphas
    matches = re.findall('[^\w\d]{2,}', nick)
    for match in matches:
        score += slowPow(10, len(match))

    # Remove balanced brackets ...
    while 1:
        nickInitial = nick
        nick = re.sub('^([^()]*)(\()(.*)(\))([^()]*)$', '\1\3\5', nick, 1)
        nick = re.sub('^([^{}]*)(\{)(.*)(\})([^{}]*)$', '\1\3\5', nick, 1)
        nick = re.sub('^([^[\]]*)(\[)(.*)(\])([^[\]]*)$', '\1\3\5', nick, 1)
        if nick == nickInitial:
            break

    # ... and punish for unmatched brackets
    unmatched = re.findall('[][(){}]', nick)
    if len(unmatched) > 0:
        score += slowPow(10, len(unmatched))

    # Punish leetspeak
    leetspeak_weights = (5, 5, 2, 5, 2, 3, 1, 2, 2, 2)
    for i in range(len(leetspeak_weights)):
        hits = re.findall(repr(i), nick)
        if (hits and len(hits) > 0):
            score += leetspeak_weights[i] * len(hits) * 30

    # An alpha caps is not lame in middle or at end, provided the first
    # alpha is caps.
    nickOriginalCase = nick
    match = re.search('^([^A-Za-z]*[A-Z].*[a-z].*?)[-_]?([A-Z])', nick)
    if match:
        nick = ''.join([nick[:match.start(2)],
                           nick[match.start(2)].lower(),
                           nick[match.start(2) + 1:]])

    match = re.search('^([^A-Za-z]*)([A-Z])([a-z])', nick)
    if match:
        nick = ''.join([nick[:match.start(2)],
                           nick[match.start(2):match.end(2)].lower(),
                           nick[match.end(2):]])

    # Punish uppercase to lowercase shifts and vice-versa, modulo
    # exceptions above
    cshifts = caseShifts(nick)
    if cshifts > 1 and re.match('.*[A-Z].*', nick):
        score += slowPow(9, cshifts)

    # Punish lame endings
    if re.match('.*[XZ][^a-zA-Z]*$', nickOriginalCase):
        score += 50

    # Punish letter to numeric shifts and vice-versa
    nshifts = numberShifts(nick)
    if nshifts > 1:
        score += slowPow(9, nshifts)

    # Punish extraneous caps
    caps = re.findall('[A-Z]', nick)
    if caps and len(caps) > 0:
        score += slowPow(7, len(caps))

    # one trailing underscore is ok. i also added a - for parasite-
    nick = re.sub('[-_]$', '', nick)

    # Punish anything that's left
    remains = re.findall('[^a-zA-Z0-9]', nick)
    if remains and len(remains) > 0:
        score += 50 * len(remains) + slowPow(9, len(remains))

    # Use an appropriate function to map [0, +inf) to [0, 100)
    percentage = 100 * (1 + math.tanh((score - 400.0) / 400.0)) * \
                 (1 - 1 / (1 + score / 5.0)) / 2

    # if it's above 99.9%, show as many digits as is interesting
    score_string = re.sub('(99\\.9*\\d|\\.\\d).*', '\\1', repr(percentage))

    bot.say('[nickometer] %s was found to be %s%% lame.' % (originalNick, score_string))
