import hashlib
from Crypto.Cipher import AES
from random import randint
from os import urandom

def encrypt(key, cleartext):
  AESEncryptionKey = key
  AESEncryptionMode = AES.MODE_CBC
  clientMessage = cleartext

  AESEncryptionKeyHashed = hashlib.sha256(AESEncryptionKey).digest()
  AESEncryptionIV = urandom(16)
  clientEncryptor = AES.new(AESEncryptionKeyHashed, AESEncryptionMode, IV=AESEncryptionIV)

  if (len(clientMessage) % 16 != 0):
    clientMessageOriginalLength = len(clientMessage)
    clientMessage = clientMessage + (16 - len(clientMessage) % 16) * str(randint(0,10))
  else:
    clientMessageOriginalLength = len(clientMessage)

  ciphertext = clientEncryptor.encrypt(clientMessage)
  return ciphertext, AESEncryptionIV, clientMessageOriginalLength
