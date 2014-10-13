from sys import exit
import re
import json
import client_encrypt
import client_decrypt

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

  cptxt,IVIV,origlen = client_encrypt.encrypt(client['clientEncryptionKey'], "jadn3ui2jk23.4@$@#$#@3488329dk,x.,d.x.;[p['wd.ekmn23']]'")
  clrtxt = client_decrypt.decrypt(client['clientEncryptionKey'],IVIV,origlen,cptxt)
  print clrtxt
