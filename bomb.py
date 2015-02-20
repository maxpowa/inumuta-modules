"""
bomb.py - Simple Willie bomb prank game
Copyright 2012, Edward Powell http://embolalia.net
Licensed under the Eiffel Forum License 2.

http://willie.dfbta.net
"""
from __future__ import unicode_literals
from willie.module import commands, unblockable, HALFOP
from random import choice, randint
from re import search
import sched
import time

colors = ['Red', 'Yellow', 'Blue', 'White', 'Black']
sch = sched.scheduler(time.time, time.sleep)
fuse = 60  # seconds
bombs = dict()


@commands('bomb')
def start(bot, trigger):
    """
    Put a bomb in the specified user's pants. They will be kicked if they
    don't guess the right wire fast enough.
    """
    if not trigger.group(2):
        return

    if trigger.sender.is_nick():
        return

    if bot.privileges[trigger.sender][trigger.nick] < HALFOP:
        bot.say('Sorry, you need to be at least a halfop to request my saboteur services.')
        return

    if bot.privileges[trigger.sender][bot.nick] < HALFOP:
        bot.say('Well this is awkward... I seem to have left my bombs at home.')
        return

    if trigger.group(2).strip() == bot.nick:
        bot.say('I\'m not gonna put a bomb in my own pants!')
        return

    global bombs
    global sch
    target = trigger.group(2).split(' ')[0]
    if target in bombs:
        bot.say('I can\'t fit another bomb in ' + target + '\'s pants!')
        return
    message = 'Hey, ' + target + '! Don\'t look but, I think there\'s a bomb in your pants. 60 second timer, 5 wires: Red, Yellow, Blue, White and Black. Which wire should I cut? Don\'t worry, I know what I\'m doing! (respond with .cutwire color)'
    bot.say(message)
    color = choice(colors)
    bot.msg(trigger.nick, 'Hey, don\'t tell %s, but the %s wire? Yeah, that\'s the one. But shh! Don\'t say anything!' % (target, color))
    code = sch.enter(fuse, 1, explode, (bot, trigger))
    bombs[target.lower()] = (color, code)
    sch.run()


@commands('cutwire')
@unblockable
def cutwire(bot, trigger):
    """
    Tells willie to cut a wire when you've been bombed.
    """
    global bombs, colors
    target = trigger.nick
    if target.lower() != bot.nick.lower() and target.lower() not in bombs:
        return
    color, code = bombs.pop(target.lower())  # remove target from bomb list
    wirecut = trigger.group(2).rstrip(' ')
    if wirecut.lower() in ('all', 'all!'):
        sch.cancel(code)  # defuse timer, execute premature detonation
        kmsg = 'Cutting ALL the wires! *boom*'
        bot.write(['KICK', trigger.sender, target], kmsg)
    elif wirecut.capitalize() not in colors:
        bot.say('I can\'t seem to find that wire, ' + target + '! You sure you\'re picking the right one? It\'s not here!')
        bombs[target.lower()] = (color, code)  # Add the target back onto the bomb list,
    elif wirecut.capitalize() == color:
        bot.say('You did it, ' + target + '! I\'ll be honest, I thought you were dead. But nope, you did it. You picked the right one. Well done.')
        sch.cancel(code)  # defuse bomb
    else:
        sch.cancel(code)  # defuse timer, execute premature detonation
        kmsg = 'No! No, that\'s the wrong one. Aww, you\'ve gone and killed yourself. Oh, that\'s... that\'s not good. No good at all, really. Wow. Sorry.'
        bot.write(['KICK', trigger.sender, target], kmsg)


def explode(bot, trigger):
    target = trigger.group(2)
    kmsg = 'Oh, come on, ' + target + '! You could\'ve at least picked one! Now you\'re dead. Guts, all over the place. You see that? This is gonna take forever to clean up...'
    bot.write(['KICK', trigger.sender, target], kmsg)
    try:
        bombs.pop(target.lower())
    except:
        pass
