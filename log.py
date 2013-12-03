#!/usr/bin/python

import sys
import time

class log:
    log_name = None
    log_level = 3

    @staticmethod
    def _log(entry,log_level):
        if log.log_level > log_level:
            print entry

        if log.log_name != None:
            with open(log.log_name,'a') as f:
                f.write("%s\n" % entry)

    @staticmethod
    def e(msg):
        entry = "[!][%s] %s" % (time.strftime("%I:%M.%S"), msg)
        log._log(entry,0)

    @staticmethod
    def i(msg):
        entry = "[%s] %s" % (time.strftime("%I:%M.%S"), msg)
        log._log(entry,1)

    @staticmethod
    def d(msg):
        entry = "[*][%s] %s" % (time.strftime("%I:%M.%S"), msg)
        log._log(entry,2)

    @staticmethod
    def init_logfile(name):
        if name == None:
            name = "log/%s.log" % time.strftime("%Y.%m.%d-%I.%M.%S")
        log.log_name = name

    @staticmethod
    def set_loglevel(level):
        log.log_level = level
