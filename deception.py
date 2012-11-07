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

import socket
import sys
import time

import irc
from config import BotConf

def process_server_cmd(s,conf,cmd):
    '''
    Process a command sent by the server.
    It does not require checking for permissions.
    '''

    print "[+] Command from user server: %s" % cmd.cmd

    action = irc.get_server_cmd(cmd.cmd)

    if action == None:
        print "[-] Command %s not found." % cmd.cmd
        return

    result = action(s,cmd)

    if result == False:
        print "[-] Unable to send response ('%s') to server." % cmd.cmd

def process_user_cmd(s,conf,cmd):
    '''
    Process a command sent byt the user
    Check if the user is in the control list for the bot or in the
    access list for the target channel.
    '''

    print "[+] Command from user '%s': %s" % (cmd.user,cmd.cmd)

    channel = None

    if cmd.target.find("#") == 0:
        channel = cmd.target
    elif cmd.args[0] != None and cmd.args[0].find('#') == 0:
        channel = cmd.args[0]

    access = -1
    if conf.check_control(cmd.user):
        access = 9
    else:
        access = conf.get_access_level(channel,cmd.user)    

    action = irc.get_user_cmd(cmd.cmd)

    if action == None:
        print "[-] Command %s not found." % cmd.cmd
        return

    if not irc.check_permission(cmd.cmd,access):
        print "[-] Operation Not Permitted."
        return

    result = action(s,cmd)

    if result == False:
        print "[-] Failed to send command '%s' from user '%s'." % (cmd.cmd,cmd.user)

def main():  
    print '[+] Loading configuration file "bot.conf"'

    conf = BotConf("bot.conf")
    
    print "[+] Connecting Bot."
    print "[+] Server: %s" % conf.server
    print "[+] Port  : %d" % conf.port

    s = irc.connect(conf.server,conf.port)

    if s == None:
        print "[-] ERROR: Unable to connect to server."
        sys.exit(0)

    if irc.handshake(s,conf.nick,conf.user,conf.name) == False:
        print "[-] ERROR: Unable to perform handshake."
        sys.exit(0)
    
    print "[+] Waiting for connection to get stable..."

    time.sleep(10)

    print "[+] Bot Connected."

    irc.join_channels(s,conf.get_channel_list())

    print "[+] Joined channels in access list."

    print "[+] Deception locked and loaded!"

    try:
        msg = s.recv(512)
        while len(msg) != 0:
            msglist = msg.split('\n')            

            for line in msglist:
                if len(line) == 0: continue

                #print "[*] " + line

                cmd = irc.parse_irc(s,line.strip())                
                if cmd == None: continue

                if cmd.server_cmd:
                    process_server_cmd(s,conf,cmd)
                else:
                    process_user_cmd(s,conf,cmd)

            msg = s.recv(512)
    except:
        pass

    print "[-] ERROR: Lost connection to the server."

    if s != None: s.close()

#Run
if __name__ == "__main__":
    main()

