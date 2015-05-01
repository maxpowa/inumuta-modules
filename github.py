# coding=utf8
"""
github.py - Inumuta Github Module
Copyright 2014 Max Gurela

 _______ __ __   __           __
|     __|__|  |_|  |--.--.--.|  |--.
|    |  |  |   _|     |  |  ||  _  |
|_______|__|____|__|__|_____||_____|

"""


from __future__ import unicode_literals
from willie import web, tools
from willie.module import commands, rule, OP, NOLIMIT, require_privilege, interval
from willie.formatting import bold, color
from willie.tools import get_timezone, format_time

import operator
from collections import deque

import os
import sys
if sys.version_info.major < 3:
    from urllib2 import HTTPError
else:
    from urllib.error import HTTPError
import json
import re
import datetime
import bottle
from threading import Thread


'''
 _______           __         __
|   |   |.-----.--|  |.--.--.|  |.-----.
|       ||  _  |  _  ||  |  ||  ||  -__|
|__|_|__||_____|_____||_____||__||_____|

'''


issueURL = (r'https?://(?:www\.)?github.com/'
             '([A-z0-9\-]+/[A-z0-9\-]+)/'
             '(?:issues|pull)/'
             '([\d]+)')
regex = re.compile(issueURL)
willie_instance = None

def configure(config):
    """
    Client id and secret can be discovered by signing up your bot at
    [https://github.com/settings/applications/new](https://github.com/settings/applications/new).

    | [github]     | example                        | purpose                               |
    | ------------ | ------------------------------ | ------------------------------------- |
    | client_id    | ao123123sf12                   | Github Client ID                      |
    | secret       | 1u3432jpqj235j2oi5oji545l34j5j | Github Client Secret                  |
    | webhook      | False                          | Webhook server state (True to enable) |
    | webhook_host | 127.0.0.1                      | Webhook listen host                   |
    | webhook_port | 3333                           | Webhook listen port                   |
    """

    if config.option('Configure github module? (You will need to register on https://github.com/settings/applications/new)', False):
        config.interactive_add('github', 'client_id', 'github client id')
        config.interactive_add('github', 'secret', 'github secret')
        config.interactive_add('github', 'webhook', False)
        config.interactive_add('github', 'webhook_host', '127.0.0.1')
        config.interactive_add('github', 'webhook_port', '3333')


def setup(willie):
    repo_url = re.compile('github\.com/([^ /]+?)/([^ /]+)/?(?!\S)')
    if not willie.memory.contains('url_callbacks'):
        willie.memory['url_callbacks'] = tools.WillieMemory()
    willie.memory['url_callbacks'][regex] = issue_info
    willie.memory['url_callbacks'][repo_url] = data_url

    if willie.config.has_section('github') and willie.config.github.webhook:
        setup_webhook(willie)


def shutdown(willie):
    shutdown_webhook(willie)


'''
 _______ ______ _____        ______                    __
|   |   |   __ \     |_     |   __ \.---.-.----.-----.|__|.-----.-----.
|   |   |      <       |    |    __/|  _  |   _|__ --||  ||     |  _  |
|_______|___|__|_______|    |___|   |___._|__| |_____||__||__|__|___  |
                                                                |_____|
'''


def fetch_api_endpoint(bot, url):
    oauth = ''
    if bot.config.github.client_id and bot.config.github.secret:
        oauth = '?client_id=%s&client_secret=%s' % (bot.config.github.client_id, bot.config.github.secret)
    return web.get(url + oauth)


@rule('.*%s.*' % issueURL)
def issue_info(bot, trigger, match=None):
    match = match or trigger
    URL = 'https://api.github.com/repos/%s/issues/%s' % (match.group(1), match.group(2))

    try:
        raw = fetch_api_endpoint(bot, URL)
    except HTTPError:
        bot.say('[Github] API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    try:
        if len(data['body'].split('\n')) > 1:
            body = data['body'].split('\n')[0] + '...'
        else:
            body = data['body'].split('\n')[0]
    except (KeyError):
        bot.say('[Github] API says this is an invalid issue. Please report this if you know it\'s a correct link!')
        return NOLIMIT

    if body.strip() == '':
        body = 'No description provided.'

    response = [
        bold('[Github]'),
        ' [',
        match.group(1),
        ' #',
        str(data['number']),
        '] ',
        data['user']['login'],
        ': ',
        data['title'],
        bold(' | '),
        body
    ]
    bot.say(''.join(response))

    #bot.say(str(data))


def get_data(bot, trigger, URL):
    try:
        raw = fetch_api_endpoint(bot, URL)
        rawLang = fetch_api_endpoint(bot, URL + '/languages')
    except HTTPError:
        bot.say('[Github] API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    langData = json.loads(rawLang).items()
    langData = sorted(langData, key=operator.itemgetter(1), reverse=True)

    if 'message' in data:
        return bot.say('[Github] %s' % data['message'])

    langColors = deque(['12', '08', '09', '13'])

    max = sum([pair[1] for pair in langData])

    data['language'] = ''
    for (key, val) in langData[:3]:
        data['language'] = data['language'] + color(str("{0:.1f}".format(float(val) / max * 100)) + '% ' + key, langColors[0]) + ' '
        langColors.rotate()

    if len(langData) > 3:
        remainder = sum([pair[1] for pair in langData[3:]])
        data['language'] = data['language'] + color(str("{0:.1f}".format(float(remainder) / max * 100)) + '% Other', langColors[0]) + ' '

    timezone = get_timezone(bot.db, bot.config, None, trigger.nick)
    if not timezone:
        timezone = 'UTC'
    data['pushed_at'] = format_time(bot.db, bot.config, timezone, trigger.nick, trigger.sender, from_utc(data['pushed_at']))

    return data


@rule(r'https?://github\.com/([^ /]+?)/([^ /]+)/?(?!\S)')
def data_url(bot, trigger):
    URL = 'https://api.github.com/repos/%s/%s' % (trigger.group(1), trigger.group(2))
    fmt_response(bot, trigger, URL, True)


@commands('github', 'gh')
def github_repo(bot, trigger, match=None):
    match = match or trigger
    repo = match.group(2) or match.group(1)

    if repo.lower() == 'status':
        current = json.loads(web.get('https://status.github.com/api/status.json'))
        lastcomm = json.loads(web.get('https://status.github.com/api/last-message.json'))

        status = current['status']
        if status == 'major':
            status = "\x02\x034Broken\x03\x02"
        elif status == 'minor':
            status = "\x02\x037Shakey\x03\x02"
        elif status == 'good':
            status = "\x02\x033Online\x03\x02"

        lstatus = lastcomm['status']
        if lstatus == 'major':
            lstatus = "\x02\x034Broken\x03\x02"
        elif lstatus == 'minor':
            lstatus = "\x02\x037Shakey\x03\x02"
        elif lstatus == 'good':
            lstatus = "\x02\x033Online\x03\x02"

        timezone = get_timezone(bot.db, bot.config, None, trigger.nick)
        if not timezone:
            timezone = 'UTC'
        lastcomm['created_on'] = format_time(bot.db, bot.config, timezone, trigger.nick, trigger.sender, from_utc(lastcomm['created_on']))

        return bot.say('[Github] Current Status: ' + status + ' | Last Message: ' + lstatus + ': ' + lastcomm['body'] + ' (' + lastcomm['created_on'] + ')')
    elif repo.lower() == 'rate-limit':
        return bot.say(fetch_api_endpoint(bot, 'https://api.github.com/rate_limit'))

    if '/' not in repo:
        repo = trigger.nick.strip() + '/' + repo
    URL = 'https://api.github.com/repos/%s' % (repo.strip())

    fmt_response(bot, trigger, URL)

    #bot.say(''.join(response))


def from_utc(utcTime, fmt="%Y-%m-%dT%H:%M:%SZ"):
    """
    Convert UTC time string to time.struct_time
    """
    return datetime.datetime.strptime(utcTime, fmt)


def fmt_response(bot, trigger, URL, from_regex=False):
    data = get_data(bot, trigger, URL)

    if not data:
        return
    #bot.say(str(data))

    response = [
        bold('[Github]'),
        ' ',
        data['full_name'],
        ' - ',
        data['description']
    ]

    if not data['language'].strip() == '':
        response.extend([' | ', data['language'].strip()])

    response.extend([
        ' | Last Push: ',
        str(data['pushed_at']),
        ' | Stargazers: ',
        str(data['stargazers_count']),
        ' | Watchers: ',
        str(data['watchers_count']),
        ' | Forks: ',
        str(data['forks_count']),
        ' | Network: ',
        str(data['network_count']),
        ' | Open Issues: ',
        str(data['open_issues'])
    ])

    if not from_regex:
        response.extend([' | ', data['html_url']])

    bot.say(''.join(response))


'''
 ________         __     __                 __
|  |  |  |.-----.|  |--.|  |--.-----.-----.|  |--.-----.
|  |  |  ||  -__||  _  ||     |  _  |  _  ||    <|__ --|
|________||_____||_____||__|__|_____|_____||__|__|_____|

'''


def setup_webhook(willie):
    global willie_instance
    willie_instance = willie
    host = willie.config.github.webhook_host
    port = willie.config.github.webhook_port

    base = StoppableWSGIRefServer(host=host,port=port)
    server = Thread(target=bottle.run, kwargs={'server':base})
    server.setDaemon(True)
    server.start()
    willie.memory['gh_webhook_server'] = base
    willie.memory['gh_webhook_thread'] = server

    conn = willie.db.connect()
    c = conn.cursor()

    try:
        c.execute('SELECT * FROM gh_hooks')
    except StandardError:
        create_table(willie, c)
        conn.commit()
    conn.close()


def create_table(bot, c):
    primary_key = '(channel, repo_name)'

    c.execute('''CREATE TABLE IF NOT EXISTS gh_hooks (
        channel TEXT,
        repo_name TEXT,
        enabled BOOL DEFAULT 1,
        url_color TINYINT DEFAULT 2,
        tag_color TINYINT DEFAULT 6,
        repo_color TINYINT DEFAULT 13,
        name_color TINYINT DEFAULT 15,
        hash_color TINYINT DEFAULT 14,
        branch_color TINYINT DEFAULT 6,
        PRIMARY KEY {0}
        )'''.format(primary_key))



def shutdown_webhook(willie):
    global willie_instance
    willie_instance = None
    if willie.memory.contains('gh_webhook_server'):
        print('Stopping webhook server')
        willie.memory['gh_webhook_server'].stop()
        willie.memory['gh_webhook_thread'].join()
        print('Github webhook shutdown complete')


class StoppableWSGIRefServer(bottle.ServerAdapter):
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


def get_targets(repo):
    conn = willie_instance.db.connect()
    c = conn.cursor()

    #willie_instance.msg('#Inumuta', 'Checking db for '+repo)
    c.execute('SELECT * FROM gh_hooks WHERE repo_name = ? AND enabled = 1', (repo,))
    result = c.fetchall()
    #willie_instance.msg('#Inumuta', 'Result: '+json.dumps(result))
    return result



@bottle.get("/webhook")
def show_hook_info():
    return 'Listening for webhook connections!'


@bottle.post("/webhook")
def webhook():
    event = bottle.request.headers.get('X-GitHub-Event') or 'ping'
    if event == 'ping':
        return json.dumps({'msg':'pong'})

    try:
        payload = bottle.request.json
    except:
        return bottle.abort(400, 'Something went wrong!')

    payload['event'] = event

    targets = get_targets(payload['repository']['full_name'])

    for row in targets:
        send_formatted_message(payload, row)

    return "OK"


@commands('gh-hook')
def configure_repo_messages(bot, trigger):
    '''
    .gh-hook <repo> [enable|disable] - Enable/disable displaying webhooks from repo in current channel (You must be a channel OP)
    You must also add http://xpw.us/webhook as a webhook on your github repo.
    '''
    if not trigger.admin:
        bot.say('Sorry, this feature isn\'t ready for your usage yet!')

    if not trigger.group(2):
        bot.say(configure_repo_messages.__doc__.strip())

    channel = trigger.sender
    repo_name = trigger.group(3)
    enabled = True if not trigger.group(4) or trigger.group(4).lower() == 'enable' else False

    conn = bot.db.connect()
    c = conn.cursor()

    c.execute('SELECT * FROM gh_hooks WHERE channel = ? AND repo_name = ?', (channel, repo_name))
    result = c.fetchone()
    if not result:
        c.execute('''INSERT INTO gh_hooks (channel, repo_name, enabled) VALUES (?, ?, ?)''', (channel, repo_name, enabled))
        bot.reply("Successfully enabled listening for {repo}'s events in {chan}.".format(chan=channel, repo=repo_name))
    else:
        c.execute('''UPDATE gh_hooks SET enabled = ? WHERE channel = ? AND repo_name = ?''', (enabled, channel, repo_name))
        bot.reply("Successfully modified the subscription to {repo}'s events".format(repo=repo_name))
    conn.commit()
    conn.close()

'''
 _______                             __   __   __
|    ___|.-----.----.--------.---.-.|  |_|  |_|__|.-----.-----.
|    ___||  _  |   _|        |  _  ||   _|   _|  ||     |  _  |
|___|    |_____|__| |__|__|__|___._||____|____|__||__|__|___  |
                                                        |_____|
'''


current_row = None
current_payload = None


def fmt_url(s, row=None):
    if not row:
        row = current_row
    return color(s, fg=row[3])


def fmt_tag(s, row=None):
    if not row:
        row = current_row
    return color(s, fg=row[4])


def fmt_repo(s, row=None):
    if not row:
        row = current_row
    return color(s, fg=row[5])


def fmt_name(s, row=None):
    if not row:
        row = current_row
    return color(s, fg=row[6])


def fmt_hash(s, row=None):
    if not row:
        row = current_row
    return color(s, fg=row[7])


def fmt_branch(s, row=None):
    if not row:
        row = current_row
    return color(s, fg=row[8])


def get_distinct_commits(payload=None):
    if not payload:
        payload = current_payload
    if payload.has_key('distinct_commits'):
        return payload['distinct_commits']
    commits = []
    for commit in payload['commits']:
        if commit['distinct'] and len(commit['message'].strip()) > 0:
            commits.append(commit)
    return commits


def get_ref_name(payload=None):
    if not payload:
        payload = current_payload

    if payload.has_key('ref_name'):
        return payload['ref_name']

    payload['ref_name'] = re.sub(r'^refs/(heads|tags)/', '', payload['ref'])
    return payload['ref_name']


def get_base_ref_name(payload=None):
    if not payload:
        payload = current_payload
    return re.sub(r'^refs/(heads|tags)/', '', payload['base_ref_name'])


def get_pusher(payload=None):
    if not payload:
        payload = current_payload
    return payload['pusher']['name'] if payload.has_key('pusher') else 'somebody'


def get_repo_name(payload=None):
    if not payload:
        payload = current_payload
    return payload['repository']['name']


def get_after_sha(payload=None):
    if not payload:
        payload = current_payload
    return payload['after'][0:6]


def get_before_sha(payload=None):
    if not payload:
        payload = current_payload
    return payload['before'][0:6]


def get_push_summary_url(payload=None):
    if not payload:
        payload = current_payload

    repo_url = payload['repository']['url']
    if payload['created'] or re.match(r'0{40}', payload['before']):
        if len(get_distinct_commits()) < 0:
            return repo_url + "/commits/" + get_ref_name()
        else:
            return payload['compare']
    elif payload['deleted']:
        return repo_url + "/commit/" + get_before_sha()
    elif payload['forced']:
        return repo_url + "/commits/" + get_ref_name()
    elif len(get_distinct_commits()) == 1:
        return get_distinct_commits()[0]['url']
    else:
        return payload['compare']



def fmt_push_summary_message(payload=None, row=None):
    if not payload:
        payload = current_payload
    if not row:
        row = current_row

    message = []
    message.append("[{}] {}".format(fmt_repo(get_repo_name()), fmt_name(get_pusher())))

    if payload['created'] or re.match(r'0{40}', payload['before']):
        if re.match(r'^refs/tags/', payload['ref']):
            message.append('tagged {} at'.format(fmt_tag(get_ref_name())))
            message.append(fmt_branch(get_base_ref_name()) if payload['base_ref'] else fmt_hash(get_after_sha()))
        else:
            message.append('created {}'.format(fmt_branch(get_ref_name())))

            if payload['base_ref']:
                message.append('from {}'.format(fmt_branch(get_base_ref_name())))
            elif len(get_distinct_commits()) == 0:
                message.append('at {}'.format(fmt_hash(get_after_sha())))

            num = len(get_distinct_commits())
            message.append('(+\002{}\017 new commit{})'.format(num, 's' if num > 1 else ''))

    elif payload['deleted'] or re.match(r'0{40}', payload['after']):
        message.append("\00304deleted\017 {} at {}".format(fmt_branch(get_ref_name()), fmt_hash(get_before_sha())))

    elif payload['forced']:
        message.append("\00304force-pushed\017 {} from {} to {}").format(
                       fmt_branch(get_ref_name()), fmt_hash(get_before_sha()), fmt_hash(get_after_sha()))

    elif len(payload['commits']) > 0 and len(get_distinct_commits()) == 0:
        if payload['base_ref']:
            message.append('merged {} into {}'.format(fmt_branch(get_base_ref_name()), fmt_branch(get_ref_name())))
        else:
            message.append('fast-forwarded {} from {} to {}'.format(
                           fmt_branch(get_ref_name()), fmt_hash(get_before_sha()), fmt_hash(get_after_sha())))

    else:
        num = len(get_distinct_commits())
        message.append("pushed \002{}\017 new commit{} to {}".format(num, 's' if num > 1 else '', fmt_branch(get_ref_name())))

    return ' '.join(message)


def fmt_commit_message(commit):
    short = commit['message'].split('\n', 2)[0]
    short = short+'...' if short != commit['message'] else short

    author = commit['author']['name']
    sha = commit['id']

    return '{}/{} {} {}: {}'.format(fmt_repo(get_repo_name()), fmt_branch(get_ref_name()), fmt_hash(sha[0:6]), fmt_name(author), short)


def fmt_commit_comment_summary(payload=None, row=None):
    if not payload:
        payload = current_payload
    if not row:
        row = current_row

    short = payload['comment']['body'].split('\r\n', 2)[0]
    short = short+'...' if short != payload['comment']['body'] else short
    return '[{}] {} comment on commit {}: {}'.format(
                  fmt_repo(payload['repository']['name']),
                  fmt_name(payload['sender']['login']),
                  fmt_hash(payload['comment']['commit_id'][0:6]),
                  short)


def fmt_issue_summary_message(payload=None):
    if not payload:
        payload = current_payload
    return '[{}] {} {} issue #{}: {}'.format(
                  fmt_repo(payload['repository']['name']),
                  fmt_name(payload['sender']['login']),
                  payload['action'],
                  payload['issue']['number'],
                  payload['issue']['title'])


def fmt_issue_comment_summary_message(payload=None):
    if not payload:
        payload = current_payload
    short = payload['comment']['body'].split('\r\n', 2)[0]
    short = short+'...' if short != payload['comment']['body'] else short
    return '[{}] {} comment on issue #{}: {}'.format(
                  fmt_repo(payload['repository']['name']),
                  fmt_name(payload['sender']['login']),
                  payload['issue']['number'],
                  short)


def fmt_pull_request_summary_message(payload=None):
    if not payload:
        payload = current_payload
    base_ref = payload['pull_request']['base']['label'].split(':')[-1]
    head_ref = payload['pull_request']['head']['label'].split(':')[-1]
    head_label = head_ref if head_ref != base_ref else payload['pull_request']['head']['label']

    return '[{}] {} {} pull request #{}: {} ({}...{})'.format(
                  fmt_repo(payload['repository']['name']),
                  fmt_name(payload['sender']['login']),
                  payload['action'],
                  payload['pull_request']['number'],
                  payload['pull_request']['title'],
                  fmt_branch(base_ref),
                  fmt_branch(head_ref))


def fmt_pull_request_review_comment_summary_message(payload=None):
    if not payload:
        payload = current_payload
    short = payload['comment']['body'].split('\r\n', 2)[0]
    short = short+'...' if short != payload['comment']['body'] else short
    sha1  = payload['comment']['commit_id']
    return '[{}] {} comment on pull request #{} {}: {}'.format(
                  fmt_repo(payload['repository']['name']),
                  fmt_name(payload['sender']['login']),
                  payload['pull_request']['number'],
                  fmt_hash(sha1[0:6]),
                  short)


def fmt_gollum_summary_message(payload=None):
    if not payload:
        payload = current_payload
    if len(payload['pages']) == 1:
        summary = None
        if payload['pages'][0].has_key('summary'):
            summary = payload['pages'][0]['summary']

        return '[{}] {} {} wiki page {}{}'.format(
                  fmt_repo(payload['repository']['name']),
                  fmt_name(payload['sender']['login']),
                  payload['pages'][0]['action'],
                  payload['pages'][0]['title'],
                  ": "+summary if summary else '')
    elif len(payload['pages']) > 1:
        counts = {}
        for page in payload['pages']:
            # Set default value to 0 and increment 1, only incrementing if key already exists
            counts[payload['pages']['action']] = counts.setdefault(payload['pages']['action'], 0) + 1
        actions = []
        for action, count in counts.iteritems():
            actions.append(action+" "+count)

        return '[{}] {} {} wiki pages'.format(
                  fmt_repo(payload['repository']['name']),
                  fmt_name(payload['sender']['login']),
                  fmt_arr_to_sentence(actions.sort()))


def fmt_arr_to_sentence(array):
    return '{} and {}'.format(', '.join(array[:-1]), array[-1])



def fmt_watch_message(payload=None):
    if not payload:
        payload = current_payload
    return '[{}] {} starred the project!'.format(
                  fmt_repo(payload['repository']['name']),
                  fmt_name(payload['sender']['login']))


def shorten_url(url):
    try:
        res, headers = web.post('http://git.io','url='+url, return_headers=True)
        return headers['location']
    except:
        return url


def send_formatted_message(payload, row):
    global current_row, current_payload
    current_payload = payload
    current_row = row

    messages = []
    if payload['event'] == 'push':
        messages.append(fmt_push_summary_message()+" "+fmt_url(shorten_url(get_push_summary_url())))
        for commit in get_distinct_commits():
            messages.append(fmt_commit_message(commit))
    elif payload['event'] == 'commit_comment':
        messages.append(fmt_commit_comment_summary()+" "+fmt_url(shorten_url(payload['comment']['html_url'])))
    elif payload['event'] == 'pull_request':
        if re.match('(open|close)', payload['action']):
            messages.append(fmt_pull_request_summary_message()+" "+fmt_url(shorten_url(payload['pull_request']['html_url'])))
    elif payload['event'] == 'pull_request_review_comment':
        messages.append(fmt_pull_request_review_comment_summary_message()+" "+fmt_url(shorten_url(payload['comment']['html_url'])))
    elif payload['event'] == 'issues':
        if re.match('(open|close)', payload['action']):
            messages.append(fmt_issue_summary_message()+" "+fmt_url(shorten_url(payload['issue']['html_url'])))
    elif payload['event'] == 'issue_comment':
        messages.append(fmt_issue_comment_summary_message()+" "+fmt_url(shorten_url(payload['comment']['html_url'])))
    elif payload['event'] == 'gollum':
        url = payload['pages'][0]['html_url'] if len(payload['pages']) else payload['repository']['url']+'/wiki'
        messages.append(fmt_gollum_summary_message()+" "+fmt_url(shorten_url(url)))
    elif payload['event'] == 'watch':
        messages.append(fmt_watch_message())

    for message in messages:
        willie_instance.msg(row[0], message)
