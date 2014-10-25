#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2014 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.

from client_colours import bcolours

def serverip_match(serverip):
    from sys import exit
    import socket
    from re import match
    try:
        socket.inet_aton(serverip)
        servername = ""
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, serverip)
            servername = ""
        except socket.error:
            if not match("^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}$", serverip):
                print bcolours.ERROR+"Server IP/domain not in correct shape, please check config."+bcolours.ENDC
                exit(0)
                #if it is a real domain, just pass it along as serverip...

    print bcolours.HEADER+"Server IP/domain set as"+bcolours.ENDC,serverip,bcolours.HEADER+"."+bcolours.ENDC
    return serverip

def serverport_match(serverport):
    if not (0 < serverport < 65536):
        print bcolours.ERROR+"Server port must be between 1-65535, please check config."+bcolours.ENDC
        exit(0)
    print bcolours.HEADER+"Server port set as"+bcolours.ENDC,serverport,bcolours.HEADER+"."+bcolours.ENDC
    return serverport

def client_checkkey(clientkey):
    if (len(clientkey) > 64) or (len(clientkey) < 6) or (' ' in clientkey):
        return False
    else:
        return True

def serverpassword_match(serverpassword):
    from re import match
    if not (match("^[A-Za-z0-9_-]+$", serverpassword)):
        return False
    if len(serverpassword) > 32:
        return False
    return True
