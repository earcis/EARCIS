import json
import requests
from time import sleep

def messageUpdater(messageUpdateJSON, lastRequestPosition):
    


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

def receiveMessage(clienthash, serverip, serverport, nocheckcert, serverpass):
    lastRequestPosition = 0
    receiverServerUrl = 'https://'+serverip+':'+str(serverport)+'/sender'
    receiverOutboundMessage = {'receiver': clienthash, 'serverpass': serverpass, 'lastposition': lastRequestPosition}
    receiverPostHeaders = {'content-type': 'application/json'}
    while True:
        if nocheckcert:
            try:
                receiverPostRequest = requests.get(receiverServerUrl, params=receiverOutboundMessage, headers=receiverPostHeaders, verify=False)
            except requests.exceptions.ConnectionError:
                print "Connection refused by remote server, check if your settings are correct."
                break
        elif not nocheckcert:
            try:
                receiverPostRequest = requests.post(receiverServerUrl, params=receiverOutboundMessage, headers=receiverPostHeaders)
            except requests.exceptions.ConnectionError:
                print "Connection refused by remote server, check if your settings are correct."
                break
            except requests.exceptions.SSLError:
                print "TLS certificate validation error. The server is presenting an invalid certificate. Only if you absolutely trust this server, set server_no_check_certificate in settings to true."
                break
        if receiverPostRequest.status_code == 403:
            print "Server rejected your refresh request, it could be you are sending requests too frequently, or you used the wrong server password."
            break
        if receiverPostRequest.status_code != 200:
            print "Unknown request error, please retry or try a different server."
            break
        messageUpdate = receiverPostRequest.json()
        lastRequestPosition = messageUpdater(messageUpdate, lastRequestPosition)
        sleep(3)
