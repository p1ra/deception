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

IRC and Bot commands.

'''

import socket
import re

import traceback

from log import log

#----------------------
# IRC Commands
#----------------------

class IrcCmd:
    ''' Generic IRC command '''
    def __init__(self,cmd,user=None,target=None,args=None,server_cmd=False):
        self.cmd = cmd
        self.user = user
        self.target = target
        self.args = args
        self.server_cmd = server_cmd

    def __str__(self):
        return "%s:%s:%s %s" % (self.target,self.user,self.cmd," ".join(self.args))

def connect(server,port):
    ''' Connect the socket  '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((server,port))
        return s
    except Exception as e:
        log.e(traceback.format_exc())
        s.close()
        return None

def handshake(s,nick,user,name):
    ''' Send user data to initialize the connection '''
    try:
        s.sendall("NICK %s\n" % nick)
        s.sendall("USER %s 0 * :%s\n" % (user,name))
        return True
    except Exception as e:
        log.e(traceback.format_exc())
        return False

def join_channels(s,channel_list):
    ''' Join all channels in the list '''
    try:
        for channel in channel_list:
            s.sendall("JOIN %s\n" % channel)
        return True
    except Exception as e:
        log.e(traceback.format_exc())
        return False

def disconnect(s,cmd=None):
    ''' Send quit message and close socket '''
    try:
        s.sendall("QUIT :\n")
        s.close()
        return True
    except Exception as e:
        log.e(traceback.format_exc())
        return False

def pong(s,cmd):
    ''' Reply to ping requests '''
    try:
        s.sendall("PONG : %s\r\n" % cmd.args[0])
    except Exception as e:
        log.e(traceback.format_exc())
        return False

def parse_irc(s,msg):
    match = re.match(r'.*PING :(\S*)$',msg)
    if match != None:
        return IrcCmd("pong",None,None,[match.group(1)],True)
    
    #search for commands in the format "!command" and check origin
    match = re.match(r':(\S+)!\S+@\S+ PRIVMSG (\S+) :!(.+)',msg)
    if match != None:
        user = match.group(1)
        target = match.group(2)
        tokens = match.group(3).split()
        cmd    = tokens[0]
        args   = tokens[1:]

        return IrcCmd(cmd,user,target,args)

    return None

#----------------------
# Bot Commands
#----------------------

def say(s,cmd):
    ''' Send a message to channel/user  '''
    try:
        dest = cmd.target
        msg = " ".join(cmd.args)
        s.sendall("PRIVMSG %s :%s\n" % (dest,msg))
        return True
    except Exception as e:
        log.e(traceback.format_exc())
        return False

def join(s,cmd):
    ''' Join a channel  '''
    try:
        channel = cmd.args[0]
        s.sendall("JOIN %s\n" % channel)
        return True
    except Exception as e:
        log.e(traceback.format_exc())
        return False

def part(s,cmd):
    ''' Part from channel  '''
    try:
        channel = cmd.args[0]
        s.sendall("PART %s\n" % channel)
        return True
    except Exception as e:
        log.e(traceback.format_exc())
        return False


def mode(s,cmd):
    ''' Set channel mode for user '''
    try:
        user = cmd.args[0]
        mode = cmd.args[1]
        s.sendall("MODE %s %s %s\n" % (cmd.target,mode,user))
        return True
    except Exception as e:
        log.e(traceback.format_exc())
        return False

def op(s,cmd):
    ''' Mode wrapper for +o '''
    cmd.args = (cmd.args[0],"+o")
    mode(s,cmd)

def deop(s,cmd):
    ''' Mode wrapper for -o '''
    cmd.args = (cmd.args[0],"-o")
    mode(s,cmd)

def voice(s,cmd):
    ''' Mode wrapper for +v '''
    cmd.args = (cmd.args[0],"+v")
    mode(s,cmd)

def devoice(s,cmd):
    ''' Mode wrapper for -v '''
    cmd.args = (cmd.args[0],"-v")
    mode(s,cmd)

def kick(s,cmd):
    ''' Set channel mode for user '''
    try:
        user = cmd.args[0]
        s.sendall("KICK %s %s\n" % (cmd.target,user))
        return True
    except Exception as e:
        log.e(traceback.format_exc())
        return False

'''
Server commands.
Format: "command_name":permission_level
'''
server_commands = {
    "pong":pong,
    }

def get_server_cmd(cmd):
    ''' Get command response for server requests  '''
    global server_commands

    if cmd not in server_commands:
        return None

    return server_commands[cmd]

'''
User commands.
Format: "command_name":(command_function,permission_level)

Permission Level:
  0 : No permission required
 >0 : Channel permission level (eg. 1 for +v 2 for +o)
  9 : Control list only

Note: The function definition and the command
      must have the same name
'''
user_commands = {
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
    }
   
def get_user_cmd(cmd):
    ''' Get command response for user requests  '''
    global user_commands

    if cmd not in user_commands:
        return None

    return user_commands[cmd][0]

def check_permission(cmd,permission):
    ''' Check permission for given command '''
    global user_commands

    if cmd not in user_commands:
        return False

    return permission >= user_commands[cmd][1]
