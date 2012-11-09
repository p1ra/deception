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

Config file management.

'''

import os
import ConfigParser

from log import log

class BotConf:
    ''' Holds the bot configuration '''
    server = "localhost"
    port = 6667

    nick = "deception"
    user = "u-decept"
    name = "n-decept"

    control_list = list()

    channels = {}

    def __init__(self,path):   
        #use None for default
        if path == None:
            path = "bot.conf"

        if os.path.exists(path):
            self.load(path)
        else:
            self.save(path)

    def load(self,path):
        ''' Load configuration from config file '''
        conf = ConfigParser.SafeConfigParser()

        try:
            f = open(path,'r')
            conf.readfp(f)

            self.server = conf.get('General','server')
            self.port = int(conf.getint('General','port'))

            self.user = conf.get('General','user')
            self.name = conf.get('General','name')
            self.nick = conf.get('General','nick')

            self.control_list = conf.get('General','control_list').split(',')

            for channel in conf.sections():                
                if channel != 'General':
                    acl = {}
                    item_list = conf.items(channel)
                    for item in item_list:
                        acl[item[0]] = item[1]

                    self.channels[channel] = acl

        except Exception as e:
            log.e(traceback.format_exc())            
            return False

        return True

    def save(self,path):
        ''' Save configuration to config file '''
        conf = ConfigParser.SafeConfigParser()
        
        conf.add_section('General')
        conf.set('General','server',self.server)
        conf.set('General','port',str(self.port))
        conf.set('General','user',self.user)
        conf.set('General','name',self.name)
        conf.set('General','nick',self.nick)
        conf.set('General','control_list',','.join(self.control_list))

        for chan in self.channels.iterkeys():
            conf.add_section(chan)
            for user in self.channels[chan].iterkeys():
                conf.set(chan,user,self.channels[chan][user])
        try:
            f = open(path,'w')
            conf.write(f)
            f.close()
        except Exception as e:
            log.e(traceback.format_exc())
            return False

        return True

    def add_to_control(self,user):
        '''Add user to bot control list'''
        if user == None:
            return False

        if user not in self.control_list:
            self.control_list.append(user)
            return True
        else:
            return False

    def remove_from_control(self,user):
        '''Remove user from bot control list'''
        if user == None:
            return False

        if user in self.control_list:
            self.control_list.remove(user)
            return True
        else:
            return False        

    def check_control(self,user):
        ''' Check if user is in th bot control list '''
        if user == None:
            return False

        return user in self.control_list        

    def add_channel(self,chan,acl):
        ''' Add channel to the bot management list'''
        if chan == None or acl == None:
            return False

        if chan not in self.channels.iterkeys():
            self.channels[chan] = acl
            return True
        else:
            return False

    def remove_channel(self,chan):
        ''' Remove channel from the bot management list '''
        if chan == None:
            return False

        if chan in self.channels.iterkeys():
            del self.channels[chan]
            return True
        else:
            return False

    def add_to_channel(self,chan,user,perm):
        ''' Add user to channel access list '''
        if chan == None or user == None or perm == None:
            return False

        if chan not in self.channels.iterkeys():
            return False

        self.channels[chan][user] = perm

        return True;

    def remove_from_channel(self,chan,user):
        ''' Remove user from channel access list '''
        if chan == None or user == None:
            return False

        if chan not in self.channels.iterkeys():
            return False

        if user not in self.channels[chan].iterkeys():
            return False

        del self.channels[chan][user]
        return True

    def get_access_level(self,chan,user):
        ''' Get access level for user in the given channel '''
        if chan == None or user == None:
            return -1

        if chan not in self.channels.iterkeys():
            return -1

        if user not in self.channels[chan].iterkeys():
            return -1

        return int(self.channels[chan][user])

    def get_channel_list(self):
        return self.channels.iterkeys()

#------------------
# Self-Test only
#------------------
def __auto_test():
    ''' Sanity check for this module '''
    print "[+] Starting auto testing."

    bot = BotConf(None)

    bot.add_to_control("nick1")
    bot.add_to_control("nick2")
    bot.add_to_control("nick3")
    bot.add_to_control("nick4")
    bot.add_to_control(None)

    bot.remove_from_control("nick4")
    bot.remove_from_control("nick5")
    bot.remove_from_control(None)

    bot.add_channel("#channel1",{})
    bot.add_channel("#channel2",{})
    bot.add_channel("#channel3",{"nick1":"1","htr":"2"})
    bot.add_channel("#channel4",{})
    bot.add_channel("#channel5",None)
    bot.add_channel(None,{})

    bot.remove_channel("#channel4")
    bot.remove_channel("#channel6")
    bot.remove_channel(None)

    bot.add_to_channel("#channel1","nick1","2")
    bot.add_to_channel("#channel1","nick2","2")
    bot.add_to_channel("#channel2","nick1","2")
    bot.add_to_channel("#channel6","nick1","2")
    bot.add_to_channel("#channel2","nick2","1")
    bot.add_to_channel("#channel2","nick3","2")
    bot.add_to_channel(None,"nick3","2")
    bot.add_to_channel("#channel2",None,"2")
    bot.add_to_channel("#channel2","nick3",None)

    bot.remove_from_channel("#channel2","nick3")
    bot.remove_from_channel("#channel2","nick4")
    bot.remove_from_channel("channel2","nick3")
    bot.remove_from_channel("channel2",None)
    bot.remove_from_channel(None,"nick3")

    bot.save("bot.conf")
    bot.load("bot.conf")

    print "[+] Auto testing done."
