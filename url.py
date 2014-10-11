# coding=utf8
"""
url.py - Willie URL title module
Copyright 2010-2011, Michael Yanovich, yanovich.net, Kenneth Sham
Copyright 2012-2013 Edward Powell
Copyright 2013      Lior Ramati (firerogue517@gmail.com)
Copyright © 2014 Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net

using built in
safety.py - Alerts about malicious URLs
Copyright © 2014, Elad Alfassa, <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.
 
This module uses virustotal.com
"""
from __future__ import unicode_literals
from __future__ import print_function

from willie import web, tools
from willie.module import commands, rule, example, interval
from willie.config import ConfigurationError
from willie.formatting import color, bold

import sys
import json
import time
import os.path
import re
 
if sys.version_info.major > 2:
    unicode = str
    from urllib.request import urlretrieve
    from urllib.parse import urlparse
else:
    from urllib import urlretrieve
    from urlparse import urlparse


url_finder = None
exclusion_char = '!'
# These are used to clean up the title tag before actually parsing it. Not the
# world's best way to do this, but it'll do for now.
title_tag_data = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
quoted_title = re.compile('[\'"]<title>[\'"]', re.IGNORECASE)
# This is another regex that presumably does something important.
re_dcc = re.compile(r'(?i)dcc\ssend')
# This sets the maximum number of bytes that should be read in order to find
# the title. We don't want it too high, or a link to a big file/stream will
# just keep downloading until there's no more memory. 640k ought to be enough
# for anybody.
max_bytes = 655360


## Safety globals
vt_base_api_url = 'https://www.virustotal.com/vtapi/v2/url/'
malware_domains = []
known_good = []
## end Safety globals

def configure(config):
    """

    | [url] | example | purpose |
    | ---- | ------- | ------- |
    | exclude | https?://git\.io/.* | A list of regular expressions for URLs for which the title should not be shown. |
    | exclusion_char | ! | A character (or string) which, when immediately preceding a URL, will stop the URL's title from being shown. |
    
    | [safety] | example | purpose |
    | ---- | ------- | ------- |
    | enabled_by_default | True | Enable safety on implicity on channels |
    | vt_api_key | ea4ca709a686edfcc96a144c224935776e2ba46b77 | VirusTotal API key |
    | known_good | youtube.com,vimeo.com,.*\.tumblr.com | list of "known good" domains to ignore |
    """
    if config.option('Exclude certain URLs from automatic title display', False):
        if not config.has_section('url'):
            config.add_section('url')
        config.add_list('url', 'exclude', 'Enter regular expressions for each URL you would like to exclude.',
            'Regex:')
        config.interactive_add('url', 'exclusion_char',
            'Prefix to suppress URL titling', '!')
    
    # Safety Module
    if config.option('Configure malicious URL protection?'):
        config.add_section('safety')
        config.add_option('safety', 'enabled_by_default', 'Enable malicious URL checking for channels by default?', True)
        config.interactive_add('safety', 'vt_api_key', 'VirusTotal API Key (not mandatory)', None)
    # End safety module


def setup(bot=None):
    global url_finder, exclusion_char

    if not bot:
        return

    if bot.config.has_option('url', 'exclude'):
        regexes = [re.compile(s) for s in
                   bot.config.url.get_list('exclude')]
    else:
        regexes = []

    # We're keeping these in their own list, rather than putting then in the
    # callbacks list because 1, it's easier to deal with modules that are still
    # using this list, and not the newer callbacks list and 2, having a lambda
    # just to pass is kinda ugly.
    if not bot.memory.contains('url_exclude'):
        bot.memory['url_exclude'] = regexes
    else:
        exclude = bot.memory['url_exclude']
        if regexes:
            exclude.append(regexes)
        bot.memory['url_exclude'] = exclude

    # Ensure that url_callbacks and last_seen_url are in memory
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = tools.WillieMemory()
    if not bot.memory.contains('last_seen_url'):
        bot.memory['last_seen_url'] = tools.WillieMemory()

    if bot.config.has_option('url', 'exclusion_char'):
        exclusion_char = bot.config.url.exclusion_char

    url_finder = re.compile(r'(?u)(%s?(?:http|https|ftp)(?:://\S+))' %
        (exclusion_char))
        
    # Safety module
    if not bot.config.has_section('safety'):
        raise ConfigurationError("Safety module not configured")
    if bot.db and not bot.db.preferences.has_columns('safety'):
        bot.db.preferences.add_columns(['safety'])
    bot.memory['safety_cache'] = tools.WillieMemory()
    for item in bot.config.safety.get_list('known_good'):
        known_good.append(re.compile(item, re.I))
 
    loc = os.path.join(bot.config.homedir, 'malwaredomains.txt')
    if os.path.isfile(loc):
        if os.path.getmtime(loc) < time.time() - 24 * 60 * 60 * 7:
            # File exists but older than one week, update
            _download_malwaredomains_db(loc)
    else:
        _download_malwaredomains_db(loc)
    with open(loc, 'r') as f:
        for line in f:
            malware_domains.append(unicode(line).strip().lower())
    # End Safety module

#################
# Safety Module #
#################

def _download_malwaredomains_db(path):
    print('Downloading malwaredomains db...')
    urlretrieve('http://mirror1.malwaredomains.com/files/justdomains', path)
    
def safety_check(bot, trigger):
    """ Check for malicious URLs """
    check = True    # Enable URL checking
    strict = False  # Strict mode: kick on malicious URL
    positives = 0   # Number of engines saying it's malicious
    total = 0       # Number of total engines
    use_vt = True   # Use VirusTotal
    if bot.config.has_section('safety'):
        check = bot.config.safety.enabled_by_default
        if check is None:
            # If not set, assume default
            check = True
        else:
            check = bool(check)
    # DB overrides config:
    if bot.db and trigger.sender.lower() in bot.db.preferences:
        setting = bot.db.preferences.get(trigger.sender.lower(), 'safety')
        if setting == 'off':
            return False # Not checking
        elif setting in ['on', 'strict', 'local', 'local strict']:
            check = True
        if setting == 'strict' or setting == 'local strict':
            strict = True
        if setting == 'local' or setting == 'local strict':
            use_vt = False
 
    if not check:
        return False # Not overriden by DB, configured default off
 
    netloc = urlparse(trigger).netloc
    if any(regex.search(netloc) for regex in known_good):
        return False # Whitelisted
 
    apikey = bot.config.safety.vt_api_key
    try:
        if apikey is not None and use_vt:
            payload = {'resource': unicode(trigger),
                       'apikey': apikey,
                       'scan': '1'}
 
            if trigger not in bot.memory['safety_cache']:
                result = web.post(vt_base_api_url+'report', payload)
                if sys.version_info.major > 2:
                    result = result.decode('utf-8')
                result = json.loads(result)
                age = time.time()
                data = {'positives': result['positives'],
                        'total': result['total'],
                        'age': age}
                bot.memory['safety_cache'][trigger] = data
                if len(bot.memory['safety_cache']) > 1024:
                    _clean_cache(bot)
            else:
                print('using cache')
                result = bot.memory['safety_cache'][trigger]
            positives = result['positives']
            total = result['total']
    except Exception as e:
        bot.debug('[safety]', e, 'debug')
        pass  # Ignoring exceptions with VT so MalwareDomains will always work
 
    if unicode(netloc).lower() in malware_domains:
        # malwaredomains is more trustworthy than some VT engines
        # therefor it gets a weight of 10 engines when calculating confidence
        positives += 10
        total += 10
 
    if positives > 1:
        # Possibly malicious URL detected!
        confidence = '{}%'.format(round((positives / total) * 100))
        msg = 'link posted by %s is possibliy malicious ' % bold(trigger.nick)
        msg += '(confidence %s - %s/%s)' % (confidence, positives, total)
        bot.say('[' + bold(color('WARNING', 'red')) + '] ' + msg)
        if strict:
            bot.write(['KICK', trigger.sender, trigger.nick, 'Posted a malicious link'])
        return True
        
    return False
    
@commands('safety')
def toggle_safety(bot, trigger):
    """ Set safety setting for channel """
    allowed_states = ['strict', 'on', 'off', 'local', 'local strict']
    if not trigger.group(2) or trigger.group(2).lower() not in allowed_states:
        options = ' / '.join(allowed_states)
        bot.reply('Available options: %s' % options)
        return
    if not bot.db:
        bot.reply('No database configured, can\'t modify settings')
        return
    if not trigger.isop and not trigger.admin:
        bot.reply('Only channel operators can change safety settings')
 
    channel = trigger.sender.lower()
    bot.db.preferences.update(channel, {'safety': trigger.group(2).lower()})
    bot.reply('Safety is now set to %s in this channel' % trigger.group(2))
 
 
# Clean the cache every day, also when > 1024 entries
@interval(24 * 60 * 60)
def _clean_cache(bot):
    """ Cleanup old entries in URL cache """
    # TODO probably should be using locks here, to make sure stuff doesn't
    # explode
    oldest_key_age = 0
    oldest_key = ''
    for key, data in willie.tools.iteritems(bot.memory['safety_cache']):
        if data['age'] > oldest_key_age:
            oldest_key_age = data['age']
            oldest_key = key
    if oldest_key in bot.memory['safety_cache']:
        del bot.memory['safety_cache'][oldest_key]

#####################
# End safety module #
#####################

@commands('title')
@example('.title http://google.com', '[ Google ] - google.com')
def title_command(bot, trigger):
    """
    Show the title or URL information for the given URL, or the last URL seen
    in this channel.
    """
    if not trigger.group(2):
        if trigger.sender not in bot.memory['last_seen_url']:
            return
        matched = check_callbacks(bot, trigger,
                                  bot.memory['last_seen_url'][trigger.sender],
                                  True)
        if matched:
            return
        else:
            urls = [bot.memory['last_seen_url'][trigger.sender]]
    else:
        urls = re.findall(url_finder, trigger)

    results = process_urls(bot, trigger, urls)
    for title, domain in results[:4]:
        bot.reply('[ %s ] - %s' % (title, domain))


@rule('(?u).*(https?://\S+).*')
def title_auto(bot, trigger):
    """
    Automatically show titles for URLs. For shortened URLs/redirects, find
    where the URL redirects to and show the title for that (or call a function
    from another module to give more information).
    """
    if re.match(bot.config.core.prefix + 'title', trigger):
        return
    urls = re.findall(url_finder, trigger)
    results = None
    try:
        results = process_urls(bot, trigger, urls)
    except Exception:
        pass
    safety_check(bot, trigger)
    bot.memory['last_seen_url'][trigger.sender] = urls[-1]
    
    if results:
        for title, domain in results[:4]:
            message = '[ %s ] - %s' % (title, domain)
            # Guard against responding to other instances of this bot.
            if message != trigger:
                bot.say(message)


def process_urls(bot, trigger, urls):
    """
    For each URL in the list, ensure that it isn't handled by another module.
    If not, find where it redirects to, if anywhere. If that redirected URL
    should be handled by another module, dispatch the callback for it.
    Return a list of (title, hostname) tuples for each URL which is not handled by
    another module.
    """

    results = []
    for url in urls:
        if not url.startswith(exclusion_char):
            # Magic stuff to account for international domain names
            try:
                url = willie.web.iri_to_uri(url)
            except:
                pass
            # First, check that the URL we got doesn't match
            matched = check_callbacks(bot, trigger, url, False)
            if matched:
                continue
            # Then see if it redirects anywhere
            new_url = follow_redirects(url)
            # Then see if the final URL matches anything
            matched = check_callbacks(bot, trigger, new_url, new_url != url)
            if matched:
                continue
            # Finally, actually show the URL
            title = find_title(url)
            if title:
                results.append((title, get_hostname(new_url or url)))
    return results


def follow_redirects(url):
    """
    Follow HTTP 3xx redirects, and return the actual URL. Return None if
    there's a problem.
    """
    try:
        connection = web.get_urllib_object(url, 60)
        url = connection.geturl() or url
        connection.close()
    except:
        return None
    return url


def check_callbacks(bot, trigger, url, run=True):
    """
    Check the given URL against the callbacks list. If it matches, and ``run``
    is given as ``True``, run the callback function, otherwise pass. Returns
    ``True`` if the url matched anything in the callbacks list.
    """
    # Check if it matches the exclusion list first
    matched = False
    try:
        matched = any(regex.search(url) for regex in bot.memory['url_exclude'])
    except Exception:
        pass
    # Then, check if there's anything in the callback list
    for regex, function in tools.iteritems(bot.memory['url_callbacks']):
        match = regex.search(url)
        if match:
            if run:
                function(bot, trigger, match)
            matched = True
    return matched


def find_title(url):
    """Return the title for the given URL."""
    try:
        content, headers = web.get(url, return_headers=True, limit_bytes=max_bytes)
    except UnicodeDecodeError:
        return # Fail silently when data can't be decoded

    # Some cleanup that I don't really grok, but was in the original, so
    # we'll keep it (with the compiled regexes made global) for now.
    content = title_tag_data.sub(r'<\1title>', content)
    content = quoted_title.sub('', content)

    start = content.find('<title>')
    end = content.find('</title>')
    if start == -1 or end == -1:
        return
    title = web.decode(content[start + 7:end])
    title = title.strip()[:200]

    title = ' '.join(title.split())  # cleanly remove multiple spaces

    # More cryptic regex substitutions. This one looks to be myano's invention.
    title = re_dcc.sub('', title)

    return title or None


def get_hostname(url):
    idx = 7
    if url.startswith('https://'):
        idx = 8
    elif url.startswith('ftp://'):
        idx = 6
    hostname = url[idx:]
    slash = hostname.find('/')
    if slash != -1:
        hostname = hostname[:slash]
    return hostname

if __name__ == "__main__":
    from willie.test_tools import run_example_tests
    run_example_tests(__file__)
