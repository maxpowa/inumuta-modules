# coding=utf8
"""
dns.py - Sopel DNS module
Copyright 2015, Maxfield Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals

from sopel.module import commands
from dns.resolver import dns


NAME_SERVER = '8.8.8.8'
ADDITIONAL_RDCLASS = 65535


@commands('dig')
def dig(bot, trigger):
    """.dig <domain> - Show dns records from the given domain name"""
    if not trigger.group(3):
        return bot.say('You must specify a domain!')
    request = dns.message.make_query(trigger.group(3), dns.rdatatype.ANY)
    request.flags |= dns.flags.AD
    request.find_rrset(request.additional, dns.name.root, ADDITIONAL_RDCLASS,
                       dns.rdatatype.OPT, create=True, force_unique=True)       
    response = dns.query.udp(request, NAME_SERVER)
    bot.say('Sending results in a PM')
    for line in str(response).split('\n'):
        bot.msg(trigger.nick, line)


@commands('rdns')
def rdns(bot, trigger):
    """.rdns <ip> - Show the hostname that the given IP will resolve to"""
    if not trigger.group(3):
        return bot.say('You must specify an IP!')
    try:
        addr = dns.reversename.from_address(trigger.group(3))
        addr = dns.resolver.query(addr, "PTR")[0]
        addr = str(addr)
        if addr[-1] == '.':
            addr = addr[:-1]
        bot.say(addr)
    except:
        bot.say('Hey dipshit, you\'re supposed to give .rdns an IP!')    
