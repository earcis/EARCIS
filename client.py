#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2014 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.

import re
import json
import socket
import threading
from sys import exit
from os import urandom
from base64 import b64encode
from hashlib import sha1
import client_encrypt
import client_decrypt
import client_servercontact
import client_utils
from client_colours import bcolours

with open('client_config.json') as clientConfigJSONFile:
    clientConfigJSONData = json.load(clientConfigJSONFile)
    if re.match(r"[^@]+@[^@]+\.[^@]+", clientConfigJSONData['client_id']):
        clientid = clientConfigJSONData['client_id']
    else:
        print bcolours.ERROR+"Error: Client ID is not a standard email address, please check client_config.json."+bcolours.ENDC
        exit(0)
    clientkey = clientConfigJSONData['client_secure_key']
    if not client_utils.client_checkkey(clientkey):
        print bcolours.ERROR+"Error: Currently, the maximum acceptable secure key length is 64 characters, without spaces. Minimum: 6."+bcolours.ENDC
        exit(0)
    if (clientConfigJSONData['server_no_check_certificate'] == "true"):
        noCheckServerCertificate = True
        print bcolours.WARNING+"Warning: You opted to not check TLS server's certificate as per config, it may cause security concerns."+bcolours.ENDC
        print
    else:
        noCheckServerCertificate = False
    if re.match(r"([+|-][0-9][0-9]?)|0", clientConfigJSONData['client_time_zone']):
        clienttimezone = clientConfigJSONData['client_time_zone']
        print bcolours.HEADER+"Your time zone from UTC is set as:"+bcolours.ENDC,clienttimezone
    else:
        print bcolours.ERROR+"Your time zone is not or incorrectly set in client_config.json; if you are in UTC, use 0, otherwise -12 ~ +12."+bcolours.ENDC
        exit(0)
    serverip = client_utils.serverip_match(clientConfigJSONData['server_ip'])
    serverport = client_utils.serverport_match(int(clientConfigJSONData['server_port']))
    if clientConfigJSONData['server_password'] != "":
        if client_utils.serverpassword_match(clientConfigJSONData['server_password']):
            serverpass = clientConfigJSONData['server_password']
            print bcolours.MESSAGE+"You have set a password for connecting to this server."+bcolours.ENDC
        else:
            print bcolours.ERROR+"Error: Server password can only contain numbers and letters, and to a maximum of 32 characters. It is negotiated with clear text on both client and server side."+bcolours.ENDC
            exit(0)
    else:
        serverpass = ""
    client = {'clientID': clientid,'clientEncryptionKey':clientkey,'clientTimeZone':clienttimezone}
    pseudoUsername = str(client['clientID'].split('@')[0])
    if clientConfigJSONData['persistent_client_hash'] == "":
        clientIDForHash = client['clientID']+sha1(urandom(10)).hexdigest()
        clientHashedID = sha1(clientIDForHash).hexdigest() #shall be validated at the server for a length of 40, regulated
        print bcolours.MESSAGE+"Your current address hash is"+bcolours.ENDC,clientHashedID,bcolours.MESSAGE+". You will use it to send and receive messages on this session."+bcolours.ENDC
        print bcolours.HEADER+"This hash will change everytime you launch EARCIS, if you want to keep it persistent, you can update client_config.json, set 'persistent_client_hash' to your current hash string. However, doing so will reduce your anonymity."+bcolours.ENDC
        print
    else:
        clientHashedID = clientConfigJSONData['persistent_client_hash']
        if not (re.match("^[A-Za-z0-9_-]+$", clientHashedID) and (len(clientHashedID) == 40)):
            print bcolours.ERROR+"Error: Your persistent hash is not accepted, please clear the persistent hash in your config."+bcolours.ENDC
            exit(0)

recipientAddressSet = False

refresh_stop = threading.Event()
refresh_stop.set()

while True:
    userCommand = False
    if not recipientAddressSet:
        print "Send Message To Hashed Address: ",
        recipientAddress = raw_input()
        if re.match("^[A-Za-z0-9_-]+$", recipientAddress) and (len(recipientAddress) == 40):
            recipientAddressSet = True
            print
            print bcolours.HEADER+"You can change your secure key (for this session only) at anytime by using /key YoUrKeYhErE"+bcolours.ENDC
            print bcolours.HEADER+"You can get a new hashed address at anytime by using /hash , even if you already have a persistent hash."+bcolours.ENDC
            print bcolours.HEADER+"To connect to a new server, use /server ServerAddress:Port ServerPassword-omit-if-empty)"+bcolours.ENDC
            print bcolours.HEADER+"To change to a new recipient, use /quit to re-enter a recipient address hash."+bcolours.ENDC
            print bcolours.HEADER+"If you have been through a network interruption, you can use /reload at any time to restart message refreshing."+bcolours.ENDC
            print
        else:
            recipientAddressSet = False
            print bcolours.ERROR+"Invalid recipient address, it should only contain numbers and letters."+bcolours.ENDC

    if recipientAddressSet == True:
        if refresh_stop.isSet():
            refresh_stop.clear()
            refreshThread = threading.Thread(target=client_servercontact.receiveMessage, args=(clientHashedID, serverip, serverport, noCheckServerCertificate, serverpass, client['clientEncryptionKey'], refresh_stop, client['clientTimeZone']))
            refreshThread.start()
        clientNewMessage = raw_input()

        if clientNewMessage == '/quit':
            recipientAddressSet = False
            print bcolours.HEADER+"Press Ctrl+D to exit program, enter a new recipient address to send a message to another user."+bcolours.ENDC
            refresh_stop.set()
            continue

        while clientNewMessage.startswith('/server'):
            userCommand = True
            newServerString = clientNewMessage.split(' ')
            if len(newServerString) == 0:
                print bcolours.HEADER+"Current server:"+bcolours.ENDC,serverip
                print bcolours.HEADER+"Current port:"+bcolours.ENDC,serverport
                break
            if (len(newServerString) > 3 or len(newServerString) < 2):
                print bcolours.WARNING+"Incorrect /server usage. To change server: /server example.com:443 or /server 10.0.0.1:443"+bcolours.ENDC
                break
            if len(newServerString) == 3:
                if client_utils.serverpassword_match(newServerString[2]):
                    serverpass = newServerString[2]
                    newServerString = newServerString[:2]
                else:
                    print bcolours.WARNING+"Warning: Server password can only contain numbers and letters, and to a maximum of 32 characters. It is negotiated with clear text on both client and server side."+bcolours.ENDC
                    break
            try:
                newServerIP = client_utils.serverip_match(newServerString[1].split(':')[0])
            except:
                print bcolours.WARNING+"Incorrect /server usage. To change server: /server example.com:443 or /server 10.0.0.1:443"+bcolours.ENDC
                break
            try:
                newServerPort = client_utils.serverport_match(int(newServerString[1].split(':')[1]))
            except:
                print bcolours.WARNING+"Incorrect /server usage. To change server: /server example.com:443 or /server 10.0.0.1:443"+bcolours.ENDC
                break
            recipientAddressSet = False
            serverip = newServerIP
            serverport = newServerPort
            refresh_stop.set()
            print '\n'*40
            break

        if clientNewMessage.startswith('/hash'):
            userCommand = True
            clientIDForHash = client['clientID']+sha1(urandom(10)).hexdigest()
            clientHashedID = sha1(clientIDForHash).hexdigest()
            print bcolours.HEADER+"Your new address hash is"+bcolours.ENDC,clientHashedID,bcolours.HEADER+". You will use it to send and receive messages on this session."+bcolours.ENDC
            refresh_stop.set()

        if clientNewMessage.startswith('/reload'):
            userCommand = True
            print bcolours.HEADER+"Messaging session is reloaded."+bcolours.ENDC
            refresh_stop.set()

        while clientNewMessage.startswith('/key'):
            userCommand = True
            newKeyString = clientNewMessage.split(' ')
            if len(newKeyString) != 2:
                print bcolours.WARNING+"Incorrect /key usage. To change secure key: /key YoUrKeYhErE"+bcolours.ENDC
                break
            if not client_utils.client_checkkey(newKeyString[1]):
                print bcolours.ERROR+"Error: Currently, the maximum acceptable secure key length is 64 characters, without spaces. Minimum: 6."+bcolours.ENDC
                break
            client['clientEncryptionKey'] = newKeyString[1]
            print '\n'*40
            print bcolours.HEADER+"New secure key accepted."+bcolours.ENDC
            refresh_stop.set()
            break

        if (clientNewMessage.startswith('/')) and (userCommand == False): #Prevent random messages started with /
            userCommand = True
            print bcolours.WARNING+"Unknown command."+bcolours.ENDC

        if not userCommand:
            clientEncryptedMessage, clientEncryptedIV, clientMessageOL = client_encrypt.encrypt(client['clientEncryptionKey'], clientNewMessage)
            clientEncryptedMessage = b64encode(clientEncryptedMessage)

            if len(clientEncryptedMessage) > 1000:
                print bcolours.WARNING+"Your message is too long to send, please use several messages to send the information."+bcolours.ENDC
                continue
            clientEncryptedIV = b64encode(clientEncryptedIV)
            if len(clientEncryptedIV) > 24:
                print bcolours.WARNING+"IV length error, please retry."+bcolours.ENDC
                continue

            clientPushReturn = client_servercontact.parsingMessage(clientHashedID, recipientAddress, clientEncryptedMessage, clientEncryptedIV, clientMessageOL, serverpass)
            clientPostReturn = client_servercontact.postMessage(clientPushReturn, serverip, serverport, noCheckServerCertificate)

            if (clientPostReturn == 500):
                print bcolours.ERROR+"The server you are requesting is experiencing issues, you may consider changing server."+bcolours.ENDC
            if (clientPostReturn == 400):
                print bcolours.ERROR+"Your request was not qualified by the server, some components of your message may be incorrect."+bcolours.ENDC
            if (clientPostReturn == 403):
                print bcolours.ERROR+"Server acknowledged your request, but refused to accept your message. This may due to you're sending messages too frequently. Or, maybe you didn't enter this server's password correctly."+bcolours.ENDC
            if (clientPostReturn == 200):
                print bcolours.SENT+"Sent."+bcolours.ENDC
