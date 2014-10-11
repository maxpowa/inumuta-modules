from willie import module

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
        bot.say(trigger.nick + ', Mirkocraft is dead. Asie is no longer doing Minecraft related things.')
    else:
        bot.say(text + ', Mirkocraft is dead. Asie is no longer doing Minecraft related things.')

@module.commands('asie')
def asie(bot, trigger):
    bot.say('pls http://puu.sh/bGfyj/488b072f12.png')
