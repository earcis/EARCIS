#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# Copyright (c) 2014 icydoge (icydoge@gmail.com)
# For full license details, see LICENSE.

import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom

def encrypt(key, cleartext, clienthash, recipienthash):
    AESEncryptionKey = key
    clientMessage = cleartext + "/msg"
    AESEncryptionKeyHashed = hashlib.sha256(AESEncryptionKey).digest()
    AESEncryptionIV = urandom(16)

    clientEncryptor = Cipher(algorithms.AES(AESEncryptionKeyHashed), modes.GCM(AESEncryptionIV), backend=default_backend()).encryptor()
    clientMessageHeader = "S/" + str(clienthash) + "/R/" + str(recipienthash)
    clientEncryptor.authenticate_additional_data(clientMessageHeader)
    ciphertext = clientEncryptor.update(clientMessage) + clientEncryptor.finalize()

    return ciphertext, AESEncryptionIV, clientEncryptor.tag
