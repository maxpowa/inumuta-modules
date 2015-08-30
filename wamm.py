# coding=utf8
"""
wamm.py - #WAMM4LYFE
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie import module
import random
import tweepy
import time

current_milli_time = lambda: int(round(time.time() * 1000))


@module.commands('wammspeak', 'ts3', 'ts')
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


@module.commands('docker')
@module.nickname_commands('docker')
def docker(bot, trigger):
    bot.say('http://i.imgur.com/syIGxF0.png')


@module.commands('under')
def underwhere(bot, trigger):
    if not trigger.group(2):
        return
    if trigger.group(2).strip() == 'where':
        bot.say('Under here: https://www.youtube.com/watch?v=_ak4rincQ5Y')


@module.commands('yuuki')
def yuuki(bot, trigger):
    """
    .yuuki [target] - Do you want to get stabbed <name>? Because I don't mind doing so.
    """
    phrases = ['Do you want to get stabbed {}? Because I don\'t mind doing so.',
               'I don\'t mind killing you right now, {}']
    if trigger.group(3):
        bot.say(random.choice(phrases).format(trigger.group(3).strip()))

last_message_id = None
last_message = None


@module.commands('opt-in')
def opt_in(bot, trigger):
    """
    .opt-in <true|false> - Opt in to your messages being tweeted by @TinyInumuta
    """
    if not trigger.group(2):
        bot.say('.opt-in <true|false> - Opt in to your messages being tweeted by @TinyInumuta')
        return

    if trigger.group(2).strip().lower() == 'true':
        bot.db.set_nick_value(trigger.nick, 'opt-in', True)
        bot.say('Your messages may occasionally be tweeted by @TinyInumuta now.')
    else:
        bot.db.set_nick_value(trigger.nick, 'opt-in', False)
        bot.say('Your messages will not be tweeted by @TinyInumuta.')


@module.rule('([^\.].*)')
def listen(bot, trigger):
    global last_message
    if trigger.sender.is_nick() or not bot.db.get_nick_value(trigger.nick, 'opt-in') or bot.db.get_channel_value(trigger.sender, 'disable-log'):
        return

    intent = 'PRIVMSG'
    if 'intent' in trigger.tags:
        intent = trigger.tags['intent']

    last_message = (trigger.nick, trigger.group(1), trigger.sender, current_milli_time(), intent)


@module.interval(3600 * 2)  # Every 2 hours, tweet the last message sent
def tweet_last_message(bot):
    global last_message_id
    if last_message:
        if last_message_id != last_message[3]:
            last_message_id = last_message[3]

            auth = tweepy.OAuthHandler(bot.config.twitter.consumer_key, bot.config.twitter.consumer_secret)
            auth.set_access_token(bot.config.twitter.access_token, bot.config.twitter.access_token_secret)
            api = tweepy.API(auth)

            padding = 6
            tmpl = '"{0}" - {1} {2}'
            if last_message[4] == 'ACTION':
                padding = 4
                tmpl = '* {1} {0} {2}'
            padding += len(last_message[2])

            extra_len = 140 - (len(last_message[0]) + padding)
            update = tmpl.format(last_message[1][:extra_len], last_message[0], last_message[2])

            if len(update) <= 140:
                api.update_status(update)
