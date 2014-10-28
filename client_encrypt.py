#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2014 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.

import hashlib
from Crypto.Cipher import AES
from os import urandom

def encrypt(key, cleartext):
    AESEncryptionKey = key
    AESEncryptionMode = AES.MODE_CBC
    clientMessage = cleartext + "/msg"

    AESEncryptionKeyHashed = hashlib.sha256(AESEncryptionKey).digest()
    AESEncryptionIV = urandom(16)
    clientEncryptor = AES.new(AESEncryptionKeyHashed, AESEncryptionMode, IV=AESEncryptionIV)

    if (len(clientMessage) % 16 != 0):
        clientMessageOriginalLength = len(clientMessage)
        clientMessage += ' ' * (16 - len(clientMessage) % 16)
    else:
        clientMessageOriginalLength = len(clientMessage)

    ciphertext = clientEncryptor.encrypt(clientMessage)
    return ciphertext, AESEncryptionIV, clientMessageOriginalLength
