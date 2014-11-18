"""
latex.py - Render LaTeX equations
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.

Uses http://quicklatex.com/
"""

from willie import web
from willie.module import commands
import re

@commands('latex')
def latex(bot, trigger):
    #Request Body
    # formula=<FORMULA>&fsize=17px&fcolor=000000&mode=0&out=1&remhost=quicklatex.com&preamble=\usepackage{amsmath}\usepackage{amsfonts}\usepackage{amssymb}
    data = web.urlencode({'formula': trigger.group(2), 'fsize': '25px', 'fcolor': '000000', 'mode': '0', 'out': '1', 'remhost': 'quicklatex.com', 'preamble': '\usepackage{amsmath}\usepackage{amsfonts}\usepackage{amssymb}'}).encode('ascii')
    url = web.post('http://quicklatex.com/latex3.f', data).split()[1]
    bot.reply(web.get('http://is.gd/create.php?format=simple&url='+url))
