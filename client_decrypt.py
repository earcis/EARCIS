#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2014 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.

import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def decrypt(key, IV, messageheader, ciphertext, messagetag):

    AESEncryptionKey = key
    AESEncryptionIV = IV
    clientCipherText = ciphertext
    AESEncryptionTag = messagetag
    clientMessageHeader = str(messageheader)

    AESEncryptionKeyHashed = hashlib.sha256(AESEncryptionKey).digest()
    clientDecryptor = Cipher(algorithms.AES(AESEncryptionKeyHashed), modes.GCM(AESEncryptionIV, AESEncryptionTag), backend=default_backend()).decryptor()
    try:
        clientDecryptor.authenticate_additional_data(clientMessageHeader)
        clearText = clientDecryptor.update(clientCipherText) + clientDecryptor.finalize()
        if clearText.endswith("/msg"):
            clearText = clearText[:(len(clearText)-4)]
            return clearText
        else:
            return False
    except:
        return False
