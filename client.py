from sys import exit
import re
import json
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
  serverip = clientConfigJSONData['server_ip'] #Todo: validating server IP
  serverport = clientConfigJSONData['server_port'] #Todo: validating server port
  client = {'clientID': clientid,'clientEncryptionKey':clientkey,'clientServerIP':serverip,'clientServerPort':serverport} #Todo: server connections

  pseudoUsername = str(client['clientID'].split('@')[0])

  #for testing only
  #cptxt,IVIV,origlen = client_encrypt.encrypt(client['clientEncryptionKey'], "jadn3ui2jk23.4@$@#$#@3488329dk,x.,d.x.;[p['wd.ekmn23']]'")
  #clrtxt = client_decrypt.decrypt(client['clientEncryptionKey'],IVIV,origlen,cptxt)

while True:
  print pseudoUsername,": ",
  clientNewMessage = raw_input()
  clientEncryptedMessage, clientEncryptedIV, clientMessageOL = client_encrypt.encrypt(client['clientEncryptionKey'], clientNewMessage)
  clientPushReturn = client_servercontact.pushMessage(clientEncryptedMessage, clientEncryptedIV, clientMessageOL) #Module not yet coded!!
