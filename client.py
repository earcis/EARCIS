from sys import exit
from os import urandom
import re
import json
from base64 import b64encode
import socket
from hashlib import sha1
import client_encrypt
import client_decrypt
import client_servercontact

#Requirements so far: Python 2.7, requests, PyCrypto.

with open('client_config.json') as clientConfigJSONFile:
  clientConfigJSONData = json.load(clientConfigJSONFile)
  if re.match(r"[^@]+@[^@]+\.[^@]+", clientConfigJSONData['client_id']):
    clientid = clientConfigJSONData['client_id']
  else:
    print "Client ID is not a standard email address, please check client_config.json."
    exit(0)
  clientkey = clientConfigJSONData['client_secure_key']
  serverip = clientConfigJSONData['server_ip']
  try:
    socket.inet_aton(serverip)
  except socket.error:
    try:
      socket.inet_pton(socket.AF_INET6, serverip)
    except socket.error:
      print "Server IP not in correct shape, please check config."
      exit(0)
  serverport = int(clientConfigJSONData['server_port'])
  if not (0 < serverport < 65536):
    print "Server port must be between 1-65535, please check config."
    exit(0)
  client = {'clientID': clientid,'clientEncryptionKey':clientkey,'clientServerIP':serverip,'clientServerPort':serverport} #Todo: server connections
  pseudoUsername = str(client['clientID'].split('@')[0])
  if clientConfigJSONData['persistent_client_hash'] == "":
    clientIDForHash = client['clientID']+sha1(urandom(10)).hexdigest()
    clientHashedID = sha1(clientIDForHash).hexdigest() #shall be validated at the server for a length of 40, regulated
    print "Your current address hash is",clientHashedID,". You will use it to send and receive messages on this session."
    print "This hash will change everytime you launch EARCIS, if you want to keep it persistent, you can update client_config.json, set 'persistent_client_hash' to your current hash string. However, doing so will reduce your anonymity."
  else:
    clientHashedID = clientConfigJSONData['persistent_client_hash']
    if not (re.match("^[A-Za-z0-9_-]+$", clientHashedID) and (len(clientHashedID) == 40)):
      print "Your persistent hash is not accepted, please clear the persistent hash in your config."
      exit(0)

recipientAddressSet = False

while True:
  if not recipientAddressSet:
    print "Send Message To Hashed Address: ",
    recipientAddress = raw_input()
    if re.match("^[A-Za-z0-9_-]+$", recipientAddress) and (len(recipientAddress) == 40):
      recipientAddressSet = True
    else:
      recipientAddressSet = False
      print "Invalid recipient address, it should only contain numbers and letters."

  if recipientAddressSet == True:
    print pseudoUsername,"to",recipientAddress,":",
    clientNewMessage = raw_input()

    if clientNewMessage == '/quit':
      recipientAddressSet = False
      print "Press Ctrl+D to exit program, enter a new recipient address to send a message to another user."
      continue

    clientEncryptedMessage, clientEncryptedIV, clientMessageOL = client_encrypt.encrypt(client['clientEncryptionKey'], clientNewMessage)
    clientEncryptedMessage = b64encode(clientEncryptedMessage)

    if len(clientEncryptedMessage) > 1000:
      print "Your message is too long to send, please use several messages to send the information."
      continue
    clientEncryptedIV = b64encode(clientEncryptedIV)
    if len(clientEncryptedIV) > 24:
      print "IV length error, please retry."
      continue

    clientPushReturn = client_servercontact.parsingMessage(clientHashedID, recipientAddress, clientEncryptedMessage, clientEncryptedIV, clientMessageOL)
    clientPostReturn = client_servercontact.postMessage(clientPushReturn, serverip, serverport)
    if (clientPostReturn == 403):
      print "Server acknowledged your request, but refused to accept your message. This may due to you're sending messages too frequently."
    if (clientPostReturn == 200):
      print "Sent."
