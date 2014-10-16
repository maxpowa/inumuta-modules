# coding=utf8
"""
hack.py - Pretend you're doing hacker-ish things (based on http://shinytoylabs.com/jargon/)
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie.module import commands
import random

abbreviations = [
    'TCP',
    'HTTP',
    'SDD',
    'RAM',
    'ASP',
    'CSS',
    'SSL',
    'AGP',
    'SQL',
    'FTP',
    'PCI',
    'VIM',
    'ADP',
    'RSS',
    'XML',
    'EXE',
    'COM',
    'HDD',
    'THX',
    'SMTP',
    'SMS',
    'USB',
    'PNG',
    'SSH',
    'WWW',
    'OSS',
    'XSS',
    'JAR'
]

adjectives = [
    'auxiliary',
    'primary',
    'back-end',
    'digital',
    'open-source',
    'virtual',
    'cross-platform',
    'redundant',
    'online',
    'haptic',
    'multi-byte',
    'bluetooth',
    'wireless',
    '1080p',
    'neural',
    'optical',
    'solid state',
    'mobile'
]

nouns = [
    'driver',
    'protocol',
    'bandwidth',
    'panel',
    'microchip',
    'program',
    'port',
    'card',
    'array',
    'interface',
    'system',
    'sensor',
    'firewall',
    'hard drive',
    'pixel',
    'alarm',
    'feed',
    'monitor',
    'application',
    'transmitter',
    'bus',
    'circuit',
    'capacitor',
    'matrix'
]

verbs = [
    'back up',
    'bypass',
    'hack',
    'override',
    'compress',
    'copy',
    'navigate',
    'index',
    'connect',
    'generate',
    'quantify',
    'calculate',
    'synthesize',
    'input',
    'transmit',
    'program',
    'reboot',
    'parse',
    'clear',
    'refresh',
    'recalibrate',
    'calibrate'
]

ingverbs = [
    'backing up',
    'bypassing',
    'hacking',
    'overriding',
    'compressing',
    'copying',
    'navigating',
    'indexing',
    'connecting',
    'generating',
    'quantifying',
    'calculating',
    'synthesizing',
    'transmitting',
    'programming',
    'parsing',
    'clearing',
    'scripting',
    'refreshing',
    'calibrating'
]

phrases = [ 
    'If we {verb} the {noun}, we can get to the {abbreviation} {noun} through the {adjective} {abbreviation} {noun}!',
    'We need to {verb} the {adjective} {abbreviation} {noun}!',
    'Try to {verb} the {abbreviation} {noun}, maybe it will {verb} the {adjective} {noun}!',
    'You can\'t {verb} the {noun} without {ingverb} the {adjective} {abbreviation} {noun}!',
    'Use the {adjective} {abbreviation} {noun}, then you can {verb} the {adjective} {noun}!',
    'The {abbreviation} {noun} is down, {verb} the {adjective} {noun} so we can {verb} the {abbreviation} {noun}!',
    '{ingverb} the {noun} won\'t do anything, we need to {verb} the {adjective} {abbreviation} {noun}!',
    'I\'ll {verb} the {adjective} {abbreviation} {noun}, that should {verb} the {abbreviation} {noun}!'
]

def sentence_cap(s):
    return s[0].upper() + s[1:]

def build_phrase(phrase):
    if '{' in phrase:
        phrase = phrase.replace('{abbreviation}', random.choice(abbreviations), 1)
        phrase = phrase.replace('{adjective}', random.choice(adjectives), 1)
        phrase = phrase.replace('{noun}', random.choice(nouns), 1)
        phrase = phrase.replace('{verb}', random.choice(verbs), 1)
        phrase = phrase.replace('{ingverb}', random.choice(ingverbs), 1)
        if '{' in phrase:
            return build_phrase(phrase)
        else:
            return sentence_cap(phrase)
    else:
        return sentence_cap(phrase)

@commands('hack')
def hack(bot, trigger):
    """
    .hack [target] - Pretend you're doing hacker-ish things (based on http://shinytoylabs.com/jargon/)
    """
    phrase = random.choice(phrases)
    if trigger.group(3):
        bot.say(trigger.group(3).strip()  + ', ' + build_phrase(phrase))
    else:
        bot.say(build_phrase(phrase))
