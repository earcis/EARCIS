import json
import requests

def parsingMessage(clienthash, recipienthash, clientmessage, clientiv, clientmessageOL):
  outboundMessage = {'recipient':recipienthash, 'sender':clienthash, 'messagebody': clientmessage, 'messageiv': clientiv, 'messagelength': clientmessageOL}
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
    except requests.exceptions.SSLError:
      print "TLS certificate validation error. The server is presenting an invalid certificate. Only if you absolutely trust this server, set server_no_check_certificate in settings to true."
    except requests.exceptions.ConnectionError:
      print "Connection refused by remote server, check if your settings are correct."
  elif not nocheckcert:
    try:
      postRequest = requests.post(serverUrl, jsonPayload, headers=postHeaders)
      return postRequest.status_code
    except requests.exceptions.ConnectionError:
      print "Connection refused by remote server, check if your settings are correct."
