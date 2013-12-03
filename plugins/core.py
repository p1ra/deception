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

Basic Bot functions

'''

# -----------
# Event hooks
# -----------

def join_channels(session):
    ''' Join all channels in the access list '''
    for channel in session.conf.channels:
        session.join(channel)

ON_CONNECT = [join_channels,]
ON_DISCONNECT = []
ON_MSG_RECV = []
ON_UNKNOWN_CMD = []
ON_PERMISSION_DENIED = []

# ----------------
# Command Handlers
# ----------------
def disconnect(session,cmd=None):
    ''' Send quit message and close socket '''
    session.disconnect()

def say(session, cmd):
    ''' Send a message to channel/user  '''
    if len(cmd.args) == 0:
        return False

    if cmd.args[0].find('#') == 0:
        dest = cmd.args[0]
        msg = " ".join(cmd.args[1:])
    elif cmd.target.find('#') == 0:
        dest = cmd.target
        msg = " ".join(cmd.args)
    else:
        dest = cmd.user
        msg = " ".join(cmd.args)

    session.privmsg(dest, msg)

    return True

def join(session, cmd):
    ''' Join a channel  '''
    if len(cmd.args) != 0 and cmd.args[0].find('#') == 0:
        channel = cmd.args[0]
    else:
        return False

    session.join(channel)

    return True

def part(session, cmd):
    ''' Part from channel  '''
    if len(cmd.args) != 0 and cmd.args[0].find('#') == 0:
        channel = cmd.args[0]
    elif cmd.target.find('#') == 0:
        channel = cmd.target
    else:
        return False

    session.part(channel) 

    return True

def mode(session, cmd):
    ''' Set channel mode for user '''
    if len(cmd.args) != 2:
        return False

    user = cmd.args[0]
    mode = cmd.args[1]

    session.mode(cmd.target,mode,user)

    return True

def op(session, cmd):
    ''' Mode wrapper for +o '''
    cmd.args = (cmd.args[0],"+o")
    return mode(session, cmd)

def deop(session, cmd):
    ''' Mode wrapper for -o '''
    cmd.args = (cmd.args[0],"-o")
    return mode(session, cmd)

def voice(session, cmd):
    ''' Mode wrapper for +v '''
    cmd.args = (cmd.args[0],"+v")
    return mode(session, cmd)

def devoice(session, cmd):
    ''' Mode wrapper for -v '''
    cmd.args = (cmd.args[0],"-v")
    return mode(session, cmd)

def kick(session, cmd):
    ''' Set channel mode for user '''
    if len(cmd.args) == 0:
        return False

    if cmd.args[0].find('#') == 0:
        dest = cmd.args[0]
        msg = " ".join(cmd.args[1:])
    elif cmd.target.find('#') == 0:
        dest = cmd.target
        msg = " ".join(cmd.args)
    else:
        return False

    session.kick(dest, user)

    return True

def sync(session, cmd):
    ''' Realod Plugins '''
    session.load_plugins()

    session.privmsg(cmd.target,"Plugins synchronized.");

    return True

'''
User commands.
Format: "command_name":(command_function,permission_level)

Permission Level:
   0 : No permission required
 1-8 : Channel permission levels (eg. 1 for +v 2 for +o)
   9 : Control list only

Note: The function definition and the command
      must have the same name
'''
COMMAND_HANDLERS = {
    "disconnect":(disconnect,9),
    "say":(say,1),
    "join":(join,9),
    "part":(part,9),
    "mode":(mode,2),
    "op":(op,2),
    "deop":(deop,2),
    "voice":(voice,2),
    "devoice":(devoice,2),
    "kick":(kick,2),
    "sync":(sync,9),
    }

