import json
import requests

def parsingMessage(clienthash, recipienthash, clientmessage, clientiv, clientmessageOL):
  outboundMessage = {'recipient':recipienthash, 'sender':clienthash, 'messagebody': clientmessage, 'messageiv': clientiv, 'messagelength': clientmessageOL}
  outboundMessageJSON = json.dumps(outboundMessage)
  return outboundMessageJSON

def postMessage(outboundPayload, serverip, serverport):
  serverUrl = 'https://'+serverip+':'+str(serverport)+'/receiver'
  jsonPayload = outboundPayload
  postHeaders = {'content-type': 'application/json'}
  try:
    postRequest = requests.post(serverUrl, jsonPayload, headers=postHeaders)
    return postRequest.status_code
  except requests.exceptions.ConnectionError:
    print "Connection refused by remote server, check if your settings are correct."
