"""
bucket.py - Yes, my interdimensional bucket stores stuff.
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""

from sopel import web
from sopel.module import commands, rule
from sopel.tools import Identifier
from sopel.formatting import color
from optparse import OptionParser
import re


def setup(bot):
    """ Set up the db structure """
    try:
        bot.db.execute('SELECT * FROM bucket_items;')
    except:
        pass
    else:
        return

    bot.db.execute('''CREATE TABLE IF NOT EXISTS bucket_items (
        ItemId INTEGER PRIMARY KEY,
        ItemName TEXT,
        ItemDesc TEXT,
        ItemCost TEXT
        )''')
    # Create the cookie item when initializing the db
    add_or_update_item(bot.db, 1, 'Cookie', 'A delicious cookie', 1.00)


def add_or_update_item(db, id=None, name=None, desc=None, cost=None):
    if name and name.startswith('"') and name.endswith('"'):
        name = name[1:-1]
    if desc and desc.startswith('"') and desc.endswith('"'):
        desc = desc[1:-1]
    if id:
        iname, idesc, icost = db.execute('SELECT ItemName,ItemDesc,ItemCost FROM bucket_items WHERE ItemId=?', (id, )).fetchone()
        if not name:
            name = iname
        if not desc:
            desc = idesc
        if not cost:
            cost = icost
        db.execute('UPDATE OR IGNORE bucket_items SET ItemName=?, ItemDesc=?, ItemCost=? WHERE ItemId=?;', (name, desc, cost, id))
        db.execute('INSERT OR IGNORE INTO bucket_items (ItemId, ItemName, ItemDesc, ItemCost) VALUES (?,?,?,?);', (id, name, desc, cost))
        return id
    else:
        return db.execute('INSERT INTO bucket_items (ItemName, ItemDesc, ItemCost) VALUES (?,?,?);', (name, desc, cost)).lastrowid


def remove_item(db, id):
    current = db.execute('SELECT ItemName,ItemDesc,ItemCost FROM bucket_items WHERE ItemId=?', (id, )).fetchone()
    db.execute('DELETE FROM bucket_items WHERE ItemId=?', (id, ))
    return current


def get_item(db, id):
    return db.execute('SELECT ItemId,ItemName,ItemDesc,ItemCost FROM bucket_items WHERE ItemId=?', (id, )).fetchone()


def find_item(db, query):
    return db.execute('SELECT ItemId,ItemName,ItemDesc,ItemCost FROM bucket_items WHERE ItemName LIKE ?', (query, )).fetchone()


def format_item(id, name, desc, cost):
    template = u"{0:<6}|{1:15}|{2:25}|{3:>8.2f}"  # column widths
    desc = ((desc[:23] + '..') if len(desc) > 25 else desc)
    return template.format(id, name, desc, float(cost))


def get_inventory_from_nick(db, nick):
    """
    Inventory is a dict of itemids with counts as the values
    """
    inventory = db.get_nick_value(nick, 'bucket_content')
    if not inventory:
        inventory = {'1': 5}  # give users 5 cookies and 100 bucks
    return inventory


def set_inventory_nick(db, nick, inv):
    """
    Inventory is a dict of itemids with counts as the values
    """
    db.set_nick_value(nick, 'bucket_content', inv)


def add_item_to_nick(db, nick, id, count=1):
    inv = get_inventory_from_nick(db, nick)
    count = int(count)
    if id in inv:
        inv[id] += count
    else:
        inv[id] = count
    set_inventory_nick(db, nick, inv)
    return True


def transfer_item_to_from_nick(db, nick_src, nick, id, count=1):
    """
    Returns boolean success/fail
    """
    if db.get_nick_id(nick_src) == db.get_nick_id(nick):
        return True
    inv_src = get_inventory_from_nick(db, nick_src)
    inv = get_inventory_from_nick(db, nick)
    count = int(count)
    if id in inv_src and inv_src[id] >= count:
        if id in inv:
            inv[id] += count
        else:
            inv[id] = count
        inv_src[id] -= count
        set_inventory_nick(db, nick_src, inv_src)
        set_inventory_nick(db, nick, inv)
        return True
    return False


@commands('colt', 'cookie')
def colt(bot, trigger):
    """
    .cookie [target] - Apparently you get a cookie
    """
    if trigger.group(3):
        if Identifier(trigger.group(3)) not in bot.privileges[trigger.sender]:
            return bot.say('I don\'t know who {} is :/'.format(trigger.group(3)))
        success = transfer_item_to_from_nick(bot.db, trigger.nick, trigger.group(3), str(1), 1)
        if success:
            bot.say('Hey, ' + trigger.group(3).strip() + '! You! You got a cookie from ' + trigger.nick + '!')
        else:
            bot.say('Oops! ' + trigger.nick + ' doesn\'t have any cookies!')


@commands('nocookie', 'nocolt')
def nocolt(bot, trigger):
    """
    .nocookie [target] - Apparently you don't get a cookie
    """
    if trigger.group(3):
        bot.say('Hey, ' + trigger.group(3).strip() + '! You don\'t get a cookie!')


@commands('give')
def give_item(bot, trigger):
    """
    .give <nick> <item> [count] - Give a user an item from your inventory. Will fail if you don't have the item, or the item doesn't exist.
    """
    if not trigger.group(2):
        return bot.say(u'[bucket] \u0F3C \u3064 \u25D5_\u25D5 \u0F3D\u3064')

    args = trigger.group(2).strip()
    admin_give = False
    if args.startswith('-o'):
        args = args.lstrip('-o').strip()
        if trigger.admin:
            admin_give = True

    result = re.match(r'^(\S+?)\s(.+?)(?:\ (\d+))?$', args)
    if not result:
        return bot.say('[bucket] Invalid parameters. .help give for more info')

    nick = result.group(1)
    if Identifier(nick) not in bot.privileges[trigger.sender] and not admin_give:
        return bot.say('[bucket] I can\'t find {}'.format(nick))
    item = find_item(bot.db, result.group(2))
    count = result.group(3) or 1

    if not item:
        return bot.say('[bucket] You can\'t transfer that item! Check .inv before trying to transfer something!')

    success = False
    if admin_give:
        success = add_item_to_nick(bot.db, nick, str(item[0]), count)
    else:
        success = transfer_item_to_from_nick(bot.db, trigger.nick, nick, str(item[0]), count)

    if success:
        bot.say(u'\u0F3C \u3064 \u25D5_\u25D5 \u0F3D\u3064 Transferred {}x {} from {} to {}.'.format(count, item[1], trigger.nick, nick))
    else:
        bot.say('[bucket] Transfer failed. Check your inventory counts before transferring! (.inv)')


@commands('inv', 'inventory')
def show_inv(bot, trigger):
    nick = trigger.nick
    if trigger.group(3):
        nick = trigger.group(3)

    inv = get_inventory_from_nick(bot.db, nick)
    response = []
    for id, count in inv.iteritems():
        id, name, desc, cost = get_item(bot.db, id)
        if count > 0:
            response.append(u'{}x {}'.format(count, name))

    bot.say(u'[bucket] {} has: {}'.format(nick, u', '.join(response)))


@commands('inspect')
def inspect_item(bot, trigger):
    """
    .inspect <item>
    """
    if not trigger.group(2):
        bot.say(u'What am I supposed to inspect?')
        return

    result = find_item(bot.db, trigger.group(2).strip())
    if result:
        id, name, desc, cost = result
        bot.say(u'{0}: {1} | ${2:.2f}'.format(name, desc, float(cost)))
    else:
        bot.say(u'Sorry, I don\'t know anything about "{}".'.format(trigger.group(2).strip()))


@commands('bucket')
def bucket_man(bot, trigger):
    """
    .bucket [options] [text...] - Create/edit bucket items, use .bucket --help for full help
    """
    if not trigger.admin:
        return

    inp = trigger.group(2)
    if not inp:
        inp = ''
    trigger_args = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', inp)
    parser = OptionParser(add_help_option=False,
                      usage='%prog [options] [text..]', prog='.bucket')
    parser.add_option('-h', '--help', action='store_true', default=False,
                      help='Show this help menu')
    parser.add_option('-p', '--peek', action='store_true', default=False,
                      help='peek at the bucket contents')
    parser.add_option('-e', '--edit', action='store_true', default=False,
                      help='edit the bucket contents')
    parser.add_option('-r', '--remove', type='int', metavar='id',
                      help='remove the item at given id')
    parser.add_option('-n', '--name', metavar='name',
                      help='name of the item to edit/create (required)')
    parser.add_option('-d', '--description', metavar='desc',
                      help='description of the item to edit/create (required)')
    parser.add_option('-i', '--id', type='int', metavar='id',
                      help='id of the item to edit/create')
    parser.add_option('-c', '--cost', type='float', default=1.00, metavar='amount',
                      help='Set the cost for the item (default: %default)')
    opts, args = parser.parse_args(trigger_args)

    if opts.help:
        if not trigger.is_privmsg:
            bot.reply("I am sending you a notice of the bucket module help")
        for line in parser.format_help().strip().splitlines():
            bot.notice(line, recipient=trigger.nick)
        return

    if opts.peek:
        content = bot.db.execute('SELECT * FROM bucket_items').fetchall()
        template = u"{0:<6}|{1:15}|{2:25}|{3:8}"  # column widths
        bot.say(template.format("ItemId", "ItemName", "ItemDesc", "ItemCost"))  # header
        bot.say(u'------|---------------|-------------------------|--------')
        for rec in content:
            bot.say(format_item(*rec))

    if opts.edit:
        if not opts.name and not opts.id:
            bot.reply('Err: Missing item name')
            return
        if not opts.description and not opts.id:
            bot.reply('Err: Missing item description')
            return
        item = add_or_update_item(bot.db, opts.id, opts.name, opts.description, opts.cost)
        bot.say(u'Added ' + format_item(*get_item(bot.db, item)))
    elif opts.remove:
        bot.say(u'Removed ' + str(remove_item(bot.db, opts.remove)))
