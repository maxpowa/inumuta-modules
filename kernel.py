# coding=utf8
"""
kernel.py - Show the current linux kernels
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel import module, web
from sopel.formatting import color
import json
import re


@module.commands('kernel')
def kernel(bot, trigger):
    """
    .kernel [branch] - Show the latest linux kernel
    """
    contents = web.get('https://www.kernel.org/releases.json')
    parsed = json.loads(contents)
    versions = []

    regex = False
    if trigger.group(2):
        regex = re.compile(r'^.*' + re.escape(trigger.group(2)) + r'.*$', re.I)

    for branch in parsed['releases']:
        if regex:
            if not regex.match(branch['moniker']) and not regex.match(branch['version']):
                continue
        versions.append('{} ({}|{})'.format(color(branch['version'], 3),
            branch['moniker'], branch['released']['isodate']))

    message = "Linux kernel versions: "
    message += ", ".join(versions)
    bot.say(message)
