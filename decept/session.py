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

from os import listdir

import time

#----------------------
# IRC Commands
#----------------------

class IrcCmd:
    ''' Generic IRC command '''
    def __init__(self,name,user=None,target=None,args=None,server_cmd=False):
        self.name = name
        self.user = user
        self.target = target
        self.args = args

    def __str__(self):
        return "%s:%s:%s %s" % (self.target,self.user,self.name," ".join(self.args))

class IrcSession:
    ''' Manages the connection to an Irc Server '''

    '''
    Server commands.
    '''
    server_commands = ["pong",]

    def __init__(self, conf):
        self.conf = conf
        self.connected = False
        self.socket = None

    def send(self,msg):
        ''' Send wrapper to handle exceptions '''
        if self.socket == None:
            return False

        try:
            self.socket.sendall(msg)
            return True
        except Exception as e:
            log.e(traceback.format_exc())
            return False

    def recv(self):
        ''' Recv wrapper to handle exceptions '''
        if self.socket == None:
            return False

        try:
            #IRC protocol uses 512 bytes as buffer size
            return self.socket.recv(512)
        except Exception as e:
            log.e(traceback.format_exc())
            return ''

    #IRC Protocol messages
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.conf.server, self.conf.port))

            self.socket.sendall("NICK %s\n" % self.conf.nick)
            self.socket.sendall("USER %s 0 * :%s\n" % (self.conf.user, self.conf.name))

            #TODO: wait for event 376`
            time.sleep(10)

            self.connected = True
        except Exception as e:
            log.e(traceback.format_exc())

            if (self.socket != None):
                self.socket.close()

    def disconnect(self,cmd=None):
        ''' Send quit message and close socket '''
        self.send("QUIT :\n")

        if self.socket != None:
            self.socket.close()

        self.connected = False

    def pong(self, cmd):
        ''' Reply to ping requests '''
        if len(cmd.args) >= 1:
            self.send("PONG : %s\r\n" % cmd.args[0])
        else:
            log.e("Missing parameter for PING message")


    def join(self, channel):
        ''' Join a channel '''
        if channel == None:
            log.e("Missing parameter for JOIN message")

        self.send("JOIN %s\n" % channel)

    def part(self, channel):
        ''' Part from channel  '''
        if channel == None:
            log.e("Missing parameter for PART message")

        self.send("PART %s\n" % channel)

    def mode(self, target, mode, user):
        ''' Set channel mode for user '''
        if target == None or mode == None or user == None:
            log.e("Missing parameters for MODE message")

        self.send("MODE %s %s %s\n" % (target, mode, user))

    def privmsg(self,target,msg):
        ''' Send a message to channel/user  '''
        if target == None or msg == None:
            log.e("Missing parameters for PRIVMSG message")

        self.send("PRIVMSG %s :%s\n" % (target, msg))

    #Plugin Support
    def on_connect(self):
        ''' Execute plugins on connect connect hooks '''
        for hook in self.on_connect_hooks:
            #Try block to avoid breaking on bugged plugins
            try:
                hook(self)
            except:
                log.e("Hook %s chashed" % hook.__name__)
                log.e(traceback.format_exc())

    def on_disconnect(self):
        ''' Execute plugins on disconnect hooks '''
        for hook in self.on_disconnect_hooks:
            #Try block to avoid breaking on bugged plugins
            try:
                hook(self)
            except:
                log.e("Hook %s chashed" % hook.__name__)
                log.e(traceback.format_exc())

    def on_msg_recv(self, msg):
        ''' Execute plugins on cmd recv hooks '''
        for hook in self.on_msg_recv_hooks:
            #Try block to avoid breaking on bugged plugins
            try:
                hook(self, msg)
            except:
                log.e("Hook %s chashed" % hook.__name__)
                log.e(traceback.format_exc())

    def on_unknown_cmd(self, cmd):
        ''' Execute plugins on cmd recv hooks '''
        for hook in self.on_unknown_cmd_hooks:
            #Try block to avoid breaking on bugged plugins
            try:
                hook(self, cmd)
            except:
                log.e("Hook %s chashed" % hook.__name__)
                log.e(traceback.format_exc())

    def on_permission_denied(self, cmd):
        ''' Execute plugins on cmd recv hooks '''
        for hook in self.on_permission_denied_hooks:
            #Try block to avoid breaking on bugged plugins
            try:
                hook(self, cmd)
            except:
                log.e("Hook %s chashed" % hook.__name__)
                log.e(traceback.format_exc())

    def load_plugin(self, name, sync=False):
        ''' Load plugin on runtime '''
        log.i("Loading plugin: '%s'" % name)

        try:
            module = __import__('plugins.' + name, fromlist=["plugins"])

            if sync: reload(module)

            #Load event hooks
            if hasattr(module, 'ON_CONNECT'):
                for hook in module.ON_CONNECT:
                    self.on_connect_hooks.append(hook)

            if hasattr(module, 'ON_DISCONNECT'):
                for hook in module.ON_DISCONNECT:
                    self.on_disconnect_hooks.append(hook)

            if hasattr(module, 'ON_MSG_RECV'):
                for hook in module.ON_MSG_RECV:
                    self.on_msg_recv_hooks.append(hook)

            if hasattr(module, 'ON_UNKNOWN_CMD'):
                for hook in module.ON_UNKNOWN_CMD:
                    self.on_unknown_cmd_hooks.append(hook)

            if hasattr(module, 'ON_PERMISSION_DENIED'):
                for hook in module.ON_PERMISSION_DENIED:
                    self.on_permission_denied_hooks.append(hook)

            #Load plugin commands
            if hasattr(module, 'COMMAND_HANDLERS'):
                for handler in module.COMMAND_HANDLERS.keys():
                    self.cmd_handlers[handler] = module.COMMAND_HANDLERS[handler]

        except:
            log.e("Unable to load plugin '%s'" % name)
            log.e(traceback.format_exc())


    def load_plugin_list(self,sync=False):
        ''' Load extra functionalities on runtime '''
        self.on_connect_hooks = []
        self.on_disconnect_hooks = []
        self.on_msg_recv_hooks = []
        self.on_unknown_cmd_hooks = []
        self.on_permission_denied_hooks = []

        self.cmd_handlers = {}

        for plugin in self.conf.plugins:
            self.load_plugin(plugin, sync)

    #Session Lifecycle
    def parse_cmd(self,msg):
        match = re.match(r'.*PING :(\S*)$',msg)
        if match != None:
            return IrcCmd("pong",None,None,[match.group(1)],True)

        #search for commands in the format "!command" and check origin
        match = re.match(r':(\S+)!\S+@\S+ PRIVMSG (\S+) :!(.+)',msg)
        if match != None:
            user = match.group(1)
            target = match.group(2)
            tokens = match.group(3).split()
            name = tokens[0]
            args = tokens[1:]

            return IrcCmd(name,user,target,args)

        return None

    def process_server_cmd(self,cmd):
        '''
        Process a command sent by the server.
        It does not require checking for permissions.
        '''
        if cmd.name not in self.server_commands:
            return False

        log.i("Command from server: %s" % cmd.name)

        result = getattr(self, cmd.name)(cmd)

        if result == False:
            log.e("Unable to send command response to server: '%s'" % cmd.name)

        return True

    def process_cmd(self,cmd):
        ''' Execute plugins commands '''
        if cmd.name not in self.cmd_handlers.keys():
            return False

        log.i("Command from user: %s" % cmd.name)

        if not self.check_permission(cmd):
            log.e("User %s does not have enough permission for command %s" % (cmd.user, cmd.name))
            return False

        #Try block to avoid breaking on bugged plugins
        try:
            result = self.cmd_handlers[cmd.name][0](self,cmd)

            if result == False:
                log.e("Unable to send command response to server: '%s'" % cmd.name)
        except:
            log.e("Command '%s' crashed." % cmd.name)
            log.e(traceback.format_exc())

        return True

    def check_permission(self, cmd):
        ''' Check permission for given command '''
        if cmd.name not in self.cmd_handlers.keys():
            return False

        if cmd.user in self.conf.control_list:
            permission = 9
        else:
            permission = 0

        return permission >= self.cmd_handlers[cmd.name][1]

    def run(self):
        self.load_plugin_list()
        log.i("Plugins Loaded.")

        self.connect()
        log.i("Bot Connected.")

        self.on_connect()
        log.i("Deception locked and loaded!")

        while self.connected:
            msg = self.recv()

            if len(msg) == 0:
                self.connected = False
                continue

            msglist = msg.split('\n')

            for line in msglist:
                if len(line) == 0: continue

                log.d(line)

                cmd = self.parse_cmd(line.strip())
                if cmd == None:
                    self.on_msg_recv(line)
                    continue

                log.d(cmd);

                if self.process_server_cmd(cmd):
                    continue

                if cmd.name not in self.cmd_handlers.keys():
                    log.e("Command '%s' not recognized." % cmd.name)
                    self.on_unknown_cmd(cmd)
                    continue

                if not self.check_permission(cmd):
                    self.on_permission_denied(cmd)

                self.process_cmd(cmd)

        self.on_disconnect()

