"""
wamm.py - #WAMM4LYFE
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from willie import module
import tweepy
import time

current_milli_time = lambda: int(round(time.time() * 1000))

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

last_message_id = None
last_message = None
    
@module.rule('(.*)')
def listen_to_wamm(bot, trigger):
    global last_message
    if trigger.sender.lower() != '#wamm' or trigger.nick.lower() != 'Teh_Colt':
        return
        
    last_message = (trigger.nick, trigger.group(1), current_milli_time())
    
@module.interval(30*60)
def tweet_last_message(bot):
    global last_message_id
    if last_message:
        if last_message_id != last_message[2]:
            last_message_id = last_message[2]
            
            auth = tweepy.OAuthHandler(bot.config.twitter.consumer_key, bot.config.twitter.consumer_secret)
            auth.set_access_token(bot.config.twitter.access_token, bot.config.twitter.access_token_secret)
            api = tweepy.API(auth)

            extra_len = 140 - (len(last_message[0])+11)
            update = '"'+last_message[1][:extra_len]+'" - '+last_message[0]+' #WAMM'
            
            if len(update) <= 140:
                api.update_status(update)
    
    