"""
wamm.py - #WAMM4LYFE
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie import module
import tweepy
import time

current_milli_time = lambda: int(round(time.time() * 1000))

def setup(bot):
    

@module.commands('wammspeak','ts3','ts')
def wammspeak(bot, trigger):
    text = trigger.group(2)
    if not text:
        bot.say(trigger.nick + ', if you already have TeamSpeak 3, go ahead and connect to ts3.everythingisawesome.us - otherwise get TeamSpeak 3 from http://www.teamspeak.com/')
    else:
        bot.say(text + ', if you already have TeamSpeak 3, go ahead and connect to ts3.everythingisawesome.us - otherwise get TeamSpeak 3 from http://www.teamspeak.com/')

@module.commands('mirkocraft')
def mirkocraft(bot, trigger):
    text = trigger.group(2)
    if not text:
        bot.say(trigger.nick + ', Mirkocraft is dead. Magnum Opis is now a thing though.')
    else:
        bot.say(text + ', Mirkocraft is dead. Magnum Opis is now a thing though.')

@module.commands('asie')
def asie(bot, trigger):
    bot.say('pls http://puu.sh/bGfyj/488b072f12.png')

@module.commands('under')
def underwhere(bot, trigger):
    if trigger.group(2) == None:
        return
    if trigger.group(2).strip() == 'where':
        bot.say('Under here: https://www.youtube.com/watch?v=_ak4rincQ5Y')

@module.commands('colt', 'cookie')
def colt(bot, trigger):
    """
    .cookie [target] - Apparently you get a cookie
    """
    if trigger.group(3):
        bot.say('Hey, ' + trigger.group(3).strip() + '! You! You got a cookie from ' + trigger.nick + '!')

@module.commands('nocookie', 'nocolt')
def nocolt(bot, trigger):
    """
    .nocookie [target] - Apparently you don't get a cookie
    """
    if trigger.group(3):
        bot.say('Hey, ' + trigger.group(3).strip() + '! You don\'t get a cookie!')
    
    