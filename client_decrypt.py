#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2014 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.

import hashlib
from Crypto.Cipher import AES

def decrypt(key, IV, originallength, ciphertext):

    AESEncryptionKey = key
    AESEncryptionMode = AES.MODE_CBC
    AESEncryptionIV = IV
    clientMessageOriginalLength = originallength
    clientCipherText = ciphertext
    AESEncryptionKeyHashed = hashlib.sha256(AESEncryptionKey).digest()
    clientDecryptor = AES.new(AESEncryptionKeyHashed, AESEncryptionMode, AESEncryptionIV)
    clearTextCut = len((16 - clientMessageOriginalLength % 16) * ' ')
    try:
        clearText = clientDecryptor.decrypt(clientCipherText)
        cutEnds = len(clearText) - clearTextCut
        clearText = clearText[:cutEnds]
        return clearText
    except:
        return False
