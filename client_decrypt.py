from Crypto.Cipher import AES
import hashlib

def decrypt(key, IV, originallength, ciphertext):

  AESEncryptionKey = key
  AESEncryptionMode = AES.MODE_CBC
  AESEncryptionIV = IV
  clientMessageOriginalLength = originallength
  clientCipherText = ciphertext
  AESEncryptionKeyHashed = hashlib.sha256(AESEncryptionKey).digest()
  clientDecryptor = AES.new(AESEncryptionKeyHashed, AESEncryptionMode, AESEncryptionIV)
  clearTextCut = len((16 - clientMessageOriginalLength % 16) * ' ')
  clearText = clientDecryptor.decrypt(clientCipherText)
  cutEnds = len(clearText) - clearTextCut
  clearText = clearText[:cutEnds]
  return clearText
