# coding=utf8
"""
playerme.py - A module for the "Facebook for gamers", player.me
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from sopel.module import commands, rule, example
from sopel.formatting import color
from sopel import tools, web
from optparse import OptionParser
import json
import re


def setup(sopel):
    user_regex = re.compile(r'player\.me\/(\w+)')
    feed_regex = re.compile(r'player\.me/feed/(\d+)')
    if not sopel.memory.contains('url_callbacks'):
        sopel.memory['url_callbacks'] = tools.SopelMemory()
    sopel.memory['url_callbacks'][user_regex] = player_me_regex
    sopel.memory['url_callbacks'][feed_regex] = player_me_feed


@commands('player')
@example('.player maxpowa')
@example('.player -g WAMM')
def player_me(bot, trigger):
    """
    .player [user] - Show information on a Player.me user
    """
    data = trigger.group(2)

    if not data:
        data = trigger.nick

    handle_input(bot, data.split(), trigger)


@rule('.*player\.me/(\w+).*')
def player_me_regex(bot, trigger):
    data = trigger.group(1)
    if 'feed' in data:
        return

    handle_input(bot, data.split(), trigger)


@rule('.*player\.me/feed/(\d+).*')
def player_me_feed(bot, trigger):
    url = 'https://player.me/api/v1/feed/' + trigger.group(1)

    try:
        raw = web.get(url)
        response = json.loads(raw)['results']
    except:
        return

    bot.say(u'[Player.me] {}: {} via {}'.format(response['user']['username'], u' '.join(response['data']['post_raw'].split()), response['source']))


def handle_input(bot, trigger_args, trigger):
    parser = OptionParser(add_help_option=False,
                      usage='%prog [options] [user]', prog='.player',
                      epilog='Since there is no easy way to discern whether a page is a group or a user simply from the url, a warning may appear when attempting to parse group urls. Simply use \'.player -g <groupname>\' for details on the group.')
    parser.add_option('-h', '--help', action='store_true', default=False,
                      help='Show this help menu')
    parser.add_option('-g', '--group', action='store_true', default=False,
                      help='Parse input as a group (default: %default)')
    parser.add_option('-b', '--bio', action='store_true', default=True,
                      help='Show the user/group bio (default: %default)')
    parser.add_option('-l', '--list', action='store_true', default=False,
                      help='Show multiple search results (default: %default)')
    parser.add_option('-p', '--page', type='int', default=1, metavar='num')
    parser.add_option('-f', '--fav_games', action='store_true', default=False,
                      help='Show the user\'s favorite games (default: %default)')
    opts, args = parser.parse_args(trigger_args)

    if opts.help:
        if not trigger.is_privmsg:
            bot.reply("I am sending you a notice of the player.me module help")
        for line in parser.format_help().strip().splitlines():
            bot.notice(line, recipient=trigger.nick)
        return

    if opts.page < 1:
        bot.say('[Player.me] Invalid page number')
        return

    if len(' '.join(args)) < 1:
        args = [trigger.nick]

    format_user(bot, opts, args)


def format_user(bot, opts, args):
    query = u' '.join(args)

    url = 'https://player.me/api/v1/users?_query={}'

    if query.isdigit():
        url = 'https://player.me/api/v1/users/{}'

    url = url.format(query)

    if opts.list:
        url = 'https://player.me/api/v1/users?_page={}&_query={}'
        url = url.format(opts.page, query)

    #bot.say('URL: '+url)
    if opts.group:
        url = url.replace('users', 'groups')
    raw = web.get(url)

    response = json.loads(raw)

    if not response['success']:
        bot.say('[Player.me] Couldn\'t find anything')
        return

    list = []
    if opts.list:
        for user in response['results']:
            list += user['username']
            list += ' ('
            list += str(user['id'])
            list += ')'
            list += ' | '
        if len(list) < 1:
            bot.say('[Player.me] No users found')
        else:
            bot.say('[Player.me] ' + u''.join(list[:-2]))
        return

    try:
        if query.isdigit():
            user = response['results']
        else:
            user = response['results'][0]
    except:
        bot.say('[Player.me] Invalid user')
        return

    if not (query.lower() == user['slug'].lower()):
        bot.say('[Player.me] No exact result found, consider using \'.player -h\' for help')
        return

    output = [
        '[Player.me] ',
        user['username'],
        ' | ',
        str(user['followers_count']),
        ' followers | ',
        str(user['following_count']),
        ' follows'
    ]

    if opts.group:
        output.pop()
        output += ' members'

    if opts.bio:
        output += ' | '
        output += u' '.join(user['description'].split())

    bot.say(''.join(output))

    if (opts.fav_games and not opts.group):
        raw = web.get('https://player.me/api/v1/users/{}/games?_liked=false'.format(user['id']))
        response = json.loads(raw)

        games = []
        try:
            results = response['results']

            for game in results:
                games += game['title']
                games += ', '

            bot.say(u'[Player.me] {}\'s favorite games: {}'.format(user['username'], u''.join(games[:-2])))

        except:
            bot.say(u'[Player.me] Unable to retrieve {}\'s favorite games'.format(user['username']))
            return
