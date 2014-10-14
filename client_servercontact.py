import json
def parsingMessage(clienthash, recipienthash, clientmessage, clientiv, clientmessageOL):
  outboundMessage = {'recipient':recipienthash, 'sender':clienthash, 'messagebody': clientmessage, 'messageiv': clientiv, 'messagelength': clientmessageOL}
  outboundMessageJSON = json.dumps(outboundMessage)
  return outboundMessageJSON
