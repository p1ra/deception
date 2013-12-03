#!/usr/bin/python

# Deception IRC Bot
#
# Copyright (C) 2012 p1ra <p1ra@smashthestack.org>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.

'''
Deception IRC Bot - by p1ra <p1ra@smashthestack.org>

Multi-purpose IRC Bot.

Features:
* Configuration file.
* Control List.
    - Users that have full access to the bot    
* Channel Access List: Users that can control.
    - Per channel user access
    - Per user mode (e.g. +v/+o) user access
'''

import sys
import signal

from decept.session import IrcSession
from decept.config import BotConf
from decept.log import log

def terminate(signal, frame):
    log.i("Exiting.")
    sys.exit(0)

def main():  
    signal.signal(signal.SIGINT, terminate)
    
    log.set_loglevel(2)
    log.init_logfile("logs")

    log.i('Loading configuration file "bot.conf"')

    conf = BotConf("bot.conf")
    
    log.i("Connecting Bot.")
    log.i("Server: %s" % conf.server)
    log.i("Port  : %d" % conf.port)

    session = IrcSession(conf)
    
    session.run()

    log.i("Exiting.")

#Run
if __name__ == "__main__":
    main()
