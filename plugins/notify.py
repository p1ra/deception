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

Notify bot error via PRIVMSG

'''

# -----------
# Event hooks
# -----------


def notify_unknown(session, cmd):
    ''' Notify Unknown command '''
    session.privmsg(cmd.target, "Unknown command: '%s'" % cmd.name)


def notify_denied(session, cmd):
    ''' Notify a permission check failure '''
    session.privmsg(cmd.target, "Permission denied for command: '%s'" %
                    cmd.name)

ON_CONNECT = []
ON_DISCONNECT = []
ON_MSG_RECV = []
ON_UNKNOWN_CMD = [notify_unknown, ]
ON_PERMISSION_DENIED = [notify_denied, ]

# ----------------
# Command Handlers
# ----------------

COMMAND_HANDLERS = {}
