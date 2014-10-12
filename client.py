from os import urandom
from sys import exit
import hashlib
from Crypto.Cipher import AES
import re
import json

with open('client_config.json') as clientConfigJSONFile:
  clientConfigJSONData = json.load(clientConfigJSONFile)
  if re.match(r"[^@]+@[^@]+\.[^@]+", clientConfigJSONData['client_id']):
    clientid = clientConfigJSONData['client_id']
  else:
    print "Client ID is not a standard email address, please check client_config.json."
    exit(0)
  clientkey = clientConfigJSONData['client_secure_key']
  #serverip = clientConfigJSONData['server_ip']
  #serverport = clientConfigJSONData['server_port']
  client = {'clientID': clientid,'clientEncryptionKey':clientkey} #Todo: server connections

AESEncryptionKey = hashlib.sha256(client['clientEncryptionKey']).digest()
AESEncryptionIV = urandom(16)     # Initialization vector: discussed later
AESEncryptionMode = AES.MODE_CBC
clientEncryptor = AES.new(AESEncryptionKey, AESEncryptionMode, IV=AESEncryptionIV)

text = '1234567890123456' #Messages MUST be encrypted in block of 16!
ciphertext = clientEncryptor.encrypt(text)
print ciphertext
