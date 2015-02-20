# coding=utf8
"""
osrc.py - A module for displaying users open source report card, https://osrc.dfm.io/
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
from __future__ import unicode_literals
import urllib2
import random
import json
from math import sqrt
from willie import web
from willie.module import commands, priority

adjectives = [
    "a high caliber",
    "a heavy hitting",
    "a serious",
    "an awesome",
    "a top notch",
    "a trend setting",
    "a champion",
    "an epic",
    "an exceptional",
    "a distinguished",
    "a noteworthy"
]

langs = {
    "Python": "Pythonista",
    "Java": "Javavore",
    "Go": "Gopher",
    "C": "low-level hacker",
    "FORTRAN": "old-school hacker",
    "JavaScript": "JavaScripter",
    "R": "useR",
    "Shell": "sysadmin",
    "ActionScript": "Flasher",
    "AppleScript": "OSXer",
    "Arduino": "hardware hacker",
    "Assembly": "hardcore hacker",
    "Awk": "AWKward scripter",
    "Objective-C": "Apple fanchild",
    "CSS": "web designer",
    "Perl": "regexer",
    "VHDL": "VHDLyzer",
    "Scala": "Scalaite",
    "C#": "C Sharper",
    "Ada": "DoD contractor",
    "Haskell": "Haskeller",
    "Clojure": "Clojurist",
    "Rust": "Rustic"
}

event_actions = {
    "CreateEvent": "creating new repositories and branches",
    "CommitCommentEvent": "commenting on your commits",
    "FollowEvent": "following other users",
    "ForkEvent": "forking other people's code",
    "IssuesEvent": "creating issues",
    "IssueCommentEvent": "commenting on issues",
    "PublicEvent": "open sourcing new projects",
    "PullRequestEvent": "submitting pull requests"
}

week_types = [
    {
      "name": "a Tuesday tinkerer",
      "vector": [1.0, 1.0, 10.0, 1.0, 1.0, 1.0, 1.0]
    },
    {
      "name": "an early-week worker",
      "vector": [1.0, 6.0, 4.0, 2.0, 1.0, 1.0, 1.0]
    },
    {
      "name": "a weekend warrior",
      "vector": [10.0, 1.0, 1.0, 1.0, 1.0, 1.0, 10.0]
    },
    {
      "name": "a hump day hero",
      "vector": [1.0, 1.0, 3.0, 10.0, 3.0, 1.0, 1.0]
    },
    {
      "name": "a late-week deadliner",
      "vector": [1.0, 1.0, 1.0, 3.0, 10.0, 1.0, 1.0]
    },
    {
      "name": "a Friday hacker",
      "vector": [1.0, 1.0, 1.0, 1.0, 1.0, 10.0, 1.0]
    },
    {
      "name": "a fulltime hacker",
      "vector": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    },
    {
      "name": "a Sunday driver",
      "vector": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 10.0]
    },
    {
      "name": "a nine-to-fiver",
      "vector": [1.0, 5.0, 5.0, 5.0, 5.0, 5.0, 1.0]
    }
]

time_of_day = [
    {"times": [0, 1], "name": "around midnight"},
    {"times": [1, 7], "name": "in the wee hours"},
    {"times": [7, 12], "name": "in the morning"},
    {"times": [12, 13], "name": "around noon"},
    {"times": [13, 18], "name": "in the afternoon"},
    {"times": [18, 21], "name": "in the evening"},
    {"times": [21, 24], "name": "late at night"}
]


@commands('osrc', 'reportcard')
@priority('high')
def os_reportcard(bot, trigger):
    """
    .osrc [nick] - If no nick is given, it will assume your IRC nick.
    """
    try:
        if not trigger.group(3):
            raw = web.get('http://osrc.dfm.io/' + trigger.nick + '.json')
            rawjson = json.loads(raw)
            usage = rawjson['usage']
            bot.say(format_text(trigger.nick, usage))
        else:
            raw = web.get('http://osrc.dfm.io/' + trigger.group(3) + '.json')
            rawjson = json.loads(raw)
            usage = rawjson['usage']
            bot.say(format_text(trigger.group(3), usage))
    except:
        bot.say('User does not have github account, or has no activity.')


def format_text(user, usage):
    user_vector = usage["week"]
    norm = sqrt(sum([v * v for v in user_vector]))
    if norm == 0:
        return 'Not enough data found for user \'' + user + '\''
    output = [
        user,
        ' is ',
        random.choice(adjectives),
        ' ',
        language(usage),
        ' who ',
        habits(usage),
        '. ',
        user,
        ' is ',
        week_type(user_vector, norm, usage),
        ' who works best ',
        best_time(usage),
        '.'
    ]
    return ''.join(output)


def best_time(usage):
    best_time = (max(enumerate(usage["day"]), key=lambda o: o[1])[0], None)
    for tod in time_of_day:
        times = tod["times"]
        if times[0] <= best_time[0] < times[1]:
            best_time = (best_time[0], tod["name"])
    if best_time[0] == 0 or best_time[0] == 12:
        return best_time[1]
    elif best_time[0] < 12:
        return best_time[1] + ' (around ' + str(best_time[0]) + ' am)'
    else:
        return str(best_time[1]) + ' (around ' + str(best_time[0] - 12) + ' pm)'


def week_type(user_vector, norm, usage):
    best_dist = -1
    week_type = None
    user_vector = [v / norm for v in user_vector]
    for week in week_types:
        vector = week["vector"]
        norm = 1.0 / sqrt(sum([v * v for v in vector]))
        dot = sum([(v * norm - w) ** 2 for v, w in zip(vector, user_vector)])
        if best_dist < 0 or dot < best_dist:
            best_dist = dot
            week_type = week["name"]
    return week_type


def language(usage):
    if not (usage['languages'] or usage['languages'][0]):
        return 'hacker'
    final = ''
    if usage['languages'][0]['language'] in langs:
        final = langs[usage['languages'][0]['language']]
    else:
        final = usage['languages'][0]['language'] + ' coder'
    if usage['languages'][0]['quantile'] < 50:
        return final + ' (one of the ' + str(usage['languages'][0]['quantile']) + '% most active ' + usage['languages'][0]['language'] + ' users)'
    else:
        return final + ' hacker'


def habits(usage):
    if usage['events'][0]['type'] in event_actions:
        return 'spends a lot of time ' + event_actions[usage['events'][0]['type']] + ' between pushes'
    else:
        return 'loves pushing code'


def main():
    raw = json.loads(urllib2.urlopen("http://osrc.dfm.io/maxpowa.json").read())
    print(raw)
    usage = raw['usage']
    print(usage)
    print(format_text('maxpowa', usage))
    print('done')

if __name__ == "__main__":
    main()
