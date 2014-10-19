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
import client_utils

#Requirements so far: Python 2.7, requests, PyCrypto.

with open('client_config.json') as clientConfigJSONFile:
  clientConfigJSONData = json.load(clientConfigJSONFile)
  if re.match(r"[^@]+@[^@]+\.[^@]+", clientConfigJSONData['client_id']):
    clientid = clientConfigJSONData['client_id']
  else:
    print "Client ID is not a standard email address, please check client_config.json."
    exit(0)
  clientkey = clientConfigJSONData['client_secure_key']
  if not client_utils.client_checkkey(clientkey):
    print "Error: Currently, the maximum acceptable secure key length is 64 characters, without spaces. Minimum: 6."
    exit(0)
  if (clientConfigJSONData['server_no_check_certificate'] == "true"):
    noCheckServerCertificate = True
    print "You opted to not check TLS server's certificate as per config, it may cause security concerns."
    print
  else:
    noCheckServerCertificate = False
  serverip = client_utils.serverip_match(clientConfigJSONData['server_ip'])
  serverport = client_utils.serverport_match(int(clientConfigJSONData['server_port']))
  client = {'clientID': clientid,'clientEncryptionKey':clientkey} #Todo: server connections
  pseudoUsername = str(client['clientID'].split('@')[0])
  if clientConfigJSONData['persistent_client_hash'] == "":
    clientIDForHash = client['clientID']+sha1(urandom(10)).hexdigest()
    clientHashedID = sha1(clientIDForHash).hexdigest() #shall be validated at the server for a length of 40, regulated
    print "Your current address hash is",clientHashedID,". You will use it to send and receive messages on this session."
    print "This hash will change everytime you launch EARCIS, if you want to keep it persistent, you can update client_config.json, set 'persistent_client_hash' to your current hash string. However, doing so will reduce your anonymity."
    print
  else:
    clientHashedID = clientConfigJSONData['persistent_client_hash']
    if not (re.match("^[A-Za-z0-9_-]+$", clientHashedID) and (len(clientHashedID) == 40)):
      print "Your persistent hash is not accepted, please clear the persistent hash in your config."
      exit(0)

recipientAddressSet = False

while True:
  userCommand = False
  if not recipientAddressSet:
    print "Send Message To Hashed Address: ",
    recipientAddress = raw_input()
    if re.match("^[A-Za-z0-9_-]+$", recipientAddress) and (len(recipientAddress) == 40):
      recipientAddressSet = True
      print
      print "You can change your secure key (for this session only) at anytime by using /key YoUrKeYhErE"
      print "You can get a new hashed address at anytime by using /hash , even if you already have a persistent hash."
      print "To connect to a new server, use /server ServerAddress:Port"
      print "To change to a new recipient, use /quit to re-enter a recipient address hash."
      print
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

    while clientNewMessage.startswith('/server'):
      userCommand = True
      newServerString = clientNewMessage.split(' ')
      if len(newServerString) == 0:
        print "Current server:",serverip
        print "Current port:",serverport
        break
      if len(newServerString) != 2:
        print "Incorrect /server usage. To change server: /server example.com:443 or /server 10.0.0.1:443"
        break
      try:
        newServerIP = client_utils.serverip_match(newServerString[1].split(':')[0])
      except:
        print "Incorrect /server usage. To change server: /server example.com:443 or /server 10.0.0.1:443"
        break
      try:
        newServerPort = client_utils.serverport_match(int(newServerString[1].split(':')[1]))
      except:
        print "Incorrect /server usage. To change server: /server example.com:443 or /server 10.0.0.1:443"
        break
      recipientAddressSet = False
      serverIP = newServerIP
      serverport = newServerPort
      break

    if clientNewMessage.startswith('/hash'):
      userCommand = True
      clientIDForHash = client['clientID']+sha1(urandom(10)).hexdigest()
      clientHashedID = sha1(clientIDForHash).hexdigest()
      print "Your new address hash is",clientHashedID,". You will use it to send and receive messages on this session."

    while clientNewMessage.startswith('/key'):
      userCommand = True
      newKeyString = clientNewMessage.split(' ')
      if len(newKeyString) != 2:
        print "Incorrect /key usage. To change secure key: /key YoUrKeYhErE"
        break
      if not client_utils.client_checkkey(newKeyString[1]):
        print "Error: Currently, the maximum acceptable secure key length is 64 characters, without spaces. Minimum: 6."
        break
      client['clientEncryptionKey'] = newKeyString[1]
      print '\n'*40
      print "New secure key accepted."
      break

    if (clientNewMessage.startswith('/')) and (userCommand == False): #Prevent random messages started with /
      userCommand = True
      print "Unknown command."

    if not userCommand:
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
      clientPostReturn = client_servercontact.postMessage(clientPushReturn, serverip, serverport, noCheckServerCertificate)
      print clientPushReturn;
      if (clientPostReturn == 500):
        print "The server you are requesting is experiencing issues, you may consider changing server."
      if (clientPostReturn == 400):
        print "Your request was not qualified by the server, some components of your message may be incorrect."
      if (clientPostReturn == 403):
        print "Server acknowledged your request, but refused to accept your message. This may due to you're sending messages too frequently."
      if (clientPostReturn == 200):
        print "Sent."
