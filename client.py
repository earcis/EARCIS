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
  clientIDForHash = client['clientID']+sha1(urandom(10)).hexdigest()
  clientHashedID = sha1(clientIDForHash).hexdigest() #shall be validated at the server for a length of 40, regulated
  print "Your current address hash is",clientHashedID,". You will use it to send and receive messages on this session."

recipientAddressSet = False

while True:
  if not recipientAddressSet:
    print "Send Message To Hashed Address: ",
    recipientAddress = raw_input()
    if re.match("^[A-Za-z0-9_-]+$", recipientAddress):
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
    clientPushReturn = client_servercontact.parsingMessage(clientHashedID, recipientAddress, b64encode(clientEncryptedMessage), b64encode(clientEncryptedIV), clientMessageOL)
    print clientPushReturn
