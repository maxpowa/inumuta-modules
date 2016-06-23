"""
8ball.py - Ask the magic 8ball a question

Licensed under the Eiffel Forum License 2.
"""
import sopel
import random


messages = [
    "Most definitely yes",
    "For sure",
    "As I see it, yes",
    "My sources say yes",
    "Yes",
    "Most likely",
    "Perhaps",
    "Maybe",
    "Not sure",
    "It is uncertain",
    "Ask me again later",
    "Don't count on it",
    "Probably not",
    "Very doubtful",
    "Most likely no",
    "Nope",
    "No",
    "My sources say no",
    "Dont even think about it",
    "Definitely no",
    "NO - It may cause disease contraction"
]


@sopel.module.commands('8', '8ball')
def eight_ball(bot, trigger):
    """
    Ask the magic 8ball a question! Usage: .8 <question>
    """
    if not trigger.group(2):
        return bot.say('A whispered "No" can be heard in the distance')
    # Seed it to the nick and message so users will get consistent answers
    random.seed(trigger.nick + trigger.group(2))
    answer = random.randint(0,len(messages) - 1)
    bot.say(messages[answer]);
