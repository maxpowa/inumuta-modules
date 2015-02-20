# coding=utf8
"""
figlet.py - A simple interface to pyfiglet
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
from willie.module import commands, rate, thread, NOLIMIT
from optparse import OptionParser
from pyfiglet import Figlet, FontNotFound

DEFAULT_FONT = 'standard'


@rate(30)
@thread(True)
@commands('figlet')
def create_figlet(bot, trigger):
    """
    .figlet [options] [text...] - Create block ascii text, use .figlet --help for full help | This command is rate limited to prevent abuse.
    """
    if not trigger.group(2):
        bot.say('You must provide text')
        return NOLIMIT
    trigger_args = trigger.group(2).split()
    parser = OptionParser(add_help_option=False,
                      usage='%prog [options] [text..]', prog='.figlet',
                      epilog='WARNING: .figlet is rate limited to 30 seconds in channels, but go nuts in PM.')
    parser.add_option('-h', '--help', action='store_true', default=False,
                      help='Show this help menu')
    parser.add_option('-f', '--font', default=DEFAULT_FONT,
                      help='font to render with (default: %default)',
                      metavar='FONT')
    parser.add_option('-D', '--direction', type='choice',
                      choices=('auto', 'left-to-right', 'right-to-left'),
                      default='auto', metavar='DIRECTION',
                      help='set direction text will be formatted in '
                           '(default: %default)')
    parser.add_option('-j', '--justify', type='choice',
                      choices=('auto', 'left', 'center', 'right'),
                      default='auto', metavar='SIDE',
                      help='set justification, defaults to print direction')
    parser.add_option('-w', '--width', type='int', default=80, metavar='COLS',
                      help='set terminal width for wrapping/justification '
                           '(default: %default)')
    parser.add_option('-r', '--reverse', action='store_true', default=False,
                      help='shows mirror image of output text')
    parser.add_option('-F', '--flip', action='store_true', default=False,
                      help='flips rendered output text over')
    parser.add_option('-l', '--list_fonts', action='store_true', default=False,
                      help='show installed fonts list')
    parser.add_option('-i', '--info_font', action='store_true', default=False,
                      help='show font\'s information, use with -f FONT')
    opts, args = parser.parse_args(trigger_args)

    if opts.help:
        if not trigger.is_privmsg:
            bot.reply("I am sending you a notice of the figlet module help")
        for line in parser.format_help().strip().splitlines():
            bot.notice(line, recipient=trigger.nick)
        return NOLIMIT

    if opts.list_fonts:
        bot.say('There\'s far too many fonts to list in IRC, but here\'s a comprehensive list (with samples!) http://irc.everythingisawesome.us/Inumuta/#figlet-fonts')
        return NOLIMIT

    if opts.info_font:
        bot.say(FigletFont.infoFont(opts.font))
        return NOLIMIT

    if len(args) == 0:
        if not trigger.is_privmsg:
            bot.reply("I am sending you a notice of the figlet module help")
        for line in parser.format_help().strip().splitlines():
            bot.notice(line, recipient=trigger.nick)
        return NOLIMIT

    text = ' '.join(args)

    r = ''
    try:
        f = Figlet(
            font=opts.font, direction=opts.direction,
            justify=opts.justify, width=opts.width,
        )
        r = f.renderText(text)
    except FontNotFound:
        bot.say('Invalid font, use .figlet -l to see a list of available fonts.')
    if opts.reverse:
        r = r.reverse()
    if opts.flip:
        r = r.flip()

    for line in (r.encode('UTF-8')).splitlines():
        bot.say(line)

    if trigger.is_privmsg:
        return NOLIMIT
