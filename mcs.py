# coding=utf8
"""
mcstatus.py - Check minecraft server status / services related things -- Uses Dinnerbone's python server status lib
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from mcstatus import MinecraftServer
from willie.module import commands
from willie import web
from willie.formatting import color,bold
import json
import re

@commands('status','ping')
def status(bot, trigger):
    """
    .status <server> - Grabs information about a minecraft server!
    """
    try:
        server = MinecraftServer.lookup(trigger.group(3).strip())
    except Exception:
        bot.say(u'[MCS] Unable to find a Minecraft server running at \'{}\''.format(trigger.group(3).strip()))
        
    try:
        status = server.status()
        desc = ' '.join(re.sub(u'\u00A7.', '', status.description).split())
        bot.say(u'[MCS] {0} | {1} players | {2} ms | {3}'.format(trigger.group(3).strip(), status.players.online, status.latency, desc))
    except Exception as e:
        try:
            raw = web.get('http://minespy.net/api/serverping/'+str(server.host)+':'+str(server.port))
            status = json.loads(raw)
            bot.say(u'[MCS] {0} | {1} players | {2} ms | {3}'.format(trigger.group(3).strip(), str(status['online']), str(status['latency']), str(status['strippedmotd'])))
        except Exception as e:
            bot.say(u'[MCS] Unable to fetch info from \'{}\' ({})'.format(trigger.group(3).strip(), e))

@commands('mcstatus','mcs')
def mcstats(bot, trigger):
    """
    .mcstatus - Check the status of Mojang's servers
    """
    try:
        raw = web.get('https://status.mojang.com/check')

        response = json.loads(raw.replace("}", "").replace("{", "").replace("]", "}").replace("[", "{"))
        
        out = []
        # use a loop so we don't have to update it if they add more servers
        for server, status in response.items():
            out.append(u'{} {} '.format(server, format_status(status)))
        bot.say(''.join(out))
    except Exception as e:
        bot.say('[MCS] Mojang server status check is currently offline. ({})'.format(e))

@commands('mcpaid','haspaid')
def mcpaid(bot, trigger):
    """
    .mcpaid <username> - Checks if <username> has a premium Minecraft account.
    """ 
    users = trigger.nick;
    if (trigger.group(2)):
        users = trigger.group(2).strip()
    for user in users.split():
        has_paid(bot, user)

def has_paid(bot, user):
    status = web.get('https://www.minecraft.net/haspaid.jsp?user={}'.format(user))
    if 'true' in status:
        bot.say('The account \'{}\' is a premium Minecraft account!'.format(user))
    else:
        bot.say('The account \'{}\' is not a premium Minecraft account!'.format(user))


def format_status(status):
    return status.replace('red', color(u'\u2718', 'red')).replace('green', color(u'\u2713', 'green')).replace('yellow', color(u'~', 'yellow'))
