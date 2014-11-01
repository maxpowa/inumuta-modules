#coding:utf8
"""
util.py - A couple of utility things
Copyright 2014 Max Gurela

Licensed under the Eiffel Forum License 2.
"""
import time

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        if args[0].config.core.show_timings: 
            args[0].notice('%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0), recipient=args[0].config.core.owner)
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap