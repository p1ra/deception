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

Kitten pictures

'''

import urllib2
import xml.etree.ElementTree as ET

# ----------------
# Command Handlers
# ----------------

def kitten(session, cmd=None):
    ''' Send kitten url '''
    data = urllib2.urlopen("http://thecatapi.com/api/images/get?format=xml").read();
    root = ET.fromstring(data)
    session.privmsg(cmd.target, root[0][0][0][0].text)

COMMAND_HANDLERS = {
    "kitten": (kitten, 0),
}
