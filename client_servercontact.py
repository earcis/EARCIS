import json
import requests
import threading
from re import match
from time import sleep
from collections import OrderedDict
from base64 import b64decode
import client_decrypt

def receiveMessage(clienthash, serverip, serverport, nocheckcert, serverpass, clientkey, stop_event):
    lastRequestPosition = 0 #Todo: lastRequestPosition is flawed!!! It will be reset after thread reinitiates, need to use time based request position tracer instead. Possibily a dictionary of sender:requesttime.
    receiverServerUrl = 'https://'+serverip+':'+str(serverport)+'/sender'
    receiverPostHeaders = {'content-type': 'application/json'}
    while (not stop_event.is_set()):
        receiverOutboundMessage = json.dumps({'receiver': clienthash, 'serverpass': serverpass, 'lastRequestPosition': lastRequestPosition})
        if nocheckcert:
            try:
                receiverPostRequest = requests.post(receiverServerUrl, receiverOutboundMessage, headers=receiverPostHeaders, verify=False)
            except requests.exceptions.ConnectionError:
                print "Connection refused by remote server, check if your settings are correct."
                break
        elif not nocheckcert:
            try:
                receiverPostRequest = requests.post(receiverServerUrl, receiverOutboundMessage, headers=receiverPostHeaders)
            except requests.exceptions.ConnectionError:
                print "Connection refused by remote server, check if your settings are correct."
                break
            except requests.exceptions.SSLError:
                print "TLS certificate validation error. The server is presenting an invalid certificate. Only if you absolutely trust this server, set server_no_check_certificate in settings to true."
                break
        if receiverPostRequest.status_code == 403:
            print "Server rejected your refresh request, it could be you are sending requests too frequently, or you used the wrong server password."
            break
        if receiverPostRequest.status_code == 404:
            stop_event.wait(3)
            continue
        if receiverPostRequest.status_code != 200:
            print "Unknown request error, please retry or try a different server."
            break
        if receiverPostRequest.status_code == 200:
            messageUpdate = receiverPostRequest.text
            lastRequestPosition = messageUpdater(messageUpdate, clientkey, lastRequestPosition)
        stop_event.wait(3)

def messageUpdater(messageUpdateJSON, securekey, lastRequestPosition):
    invalidMessageCounter = 0
    messageCounter = 0
    messageJSON = json.loads(messageUpdateJSON, object_pairs_hook=OrderedDict)
    for messageitem in messageJSON["messages"]:
        messageCounter = messageCounter + 1
        if match("^[A-Za-z0-9_-]+$", messageitem["sender"]) and (len(messageitem["sender"]) == 40):
            messagetime = messageitem["messagetime"]
            sender = messageitem["sender"]
            messagebody = b64decode(messageitem["messagebody"])
            messageiv = b64decode(messageitem["messageiv"])
            messageol = int(messageitem["messageol"])
            messagetext = client_decrypt.decrypt(securekey, messageiv, messageol, messagebody)
            if messagetext == False:
                invalidMessageCounter = invalidMessageCounter + 1
            else:
                print messagetime[11:],sender,"to you:",messagetext
        else:
            invalidMessageCounter = invalidMessageCounter + 1

    if messageJSON["messagequantity"] == 50:
        lastRequestPosition = lastRequestPosition + 50
    else:
        lastRequestPosition = lastRequestPosition + messageCounter
    return lastRequestPosition

def parsingMessage(clienthash, recipienthash, clientmessage, clientiv, clientmessageOL, serverpass):
    outboundMessage = {'recipient':recipienthash, 'sender':clienthash, 'messagebody': clientmessage, 'messageiv': clientiv, 'messagelength': clientmessageOL, 'serverpass': serverpass}
    outboundMessageJSON = json.dumps(outboundMessage)
    return outboundMessageJSON

def postMessage(outboundPayload, serverip, serverport, nocheckcert):
    serverUrl = 'https://'+serverip+':'+str(serverport)+'/receiver'
    jsonPayload = outboundPayload
    postHeaders = {'content-type': 'application/json'}
    if nocheckcert:
        try:
            postRequest = requests.post(serverUrl, jsonPayload, headers=postHeaders, verify=False)
            return postRequest.status_code
        except requests.exceptions.ConnectionError:
            print "Connection refused by remote server, check if your settings are correct."
    elif not nocheckcert:
        try:
            postRequest = requests.post(serverUrl, jsonPayload, headers=postHeaders)
            return postRequest.status_code
        except requests.exceptions.SSLError:
            print "TLS certificate validation error. The server is presenting an invalid certificate. Only if you absolutely trust this server, set server_no_check_certificate in settings to true."
        except requests.exceptions.ConnectionError:
            print "Connection refused by remote server, check if your settings are correct."
