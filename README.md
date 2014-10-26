EARCIS
======

Encryption and Relational Communications in Space

EARCIS is a instant messaging tool for secured end-to-end communications through insecure connections.

Installation and Running
--------------

Please note: EARCIS requires a server to relay messages, please find EARCIS-server at https://github.com/earcis/EARCIS-server

EARCIS requires Python 2.7, [Requests](http://docs.python-requests.org) and [PyCrypto](https://pypi.python.org/pypi/pycrypto). Please install them before installing EARCIS. If you have pip installed, you can directly use:
```sh
pip install PyCrypto
pip install requests
```
to install them.

##### Clone git repo or download a zip file.

```sh
git clone https://github.com/earcis/EARCIS.git EARCIS
cd EARCIS

```

##### Configure EARCIS by editing ```client_config.json```:

```json
{
"client_id": "yourname@example.com", 
"client_secure_key": "Your_Length_And_Complicated_Key_Here",
"client_time_zone": "+8",
"server_ip": "earcis.example.com",
"server_port": "1008",
"server_password": "PasswordOfServer",
"server_no_check_certificate": "false",
"persistent_client_hash": ""
}
```
**client_id**: An email address in valid form here, as the seed for client address hashes.

**client_secure_key**: The secure key **only** shared between you and your partner in communication, should be shared beforehand in a secured way, it is the base EARCIS is operating on.

**client_time_zone**: Your timezone relative to UTC, for your convenience (time tagging) only. For example, Shanghai is UTC +8, then use "+8" in config.

**server_ip**: The domain or IP address of the server you are connecting to. For example, "earcis.example.com" or "200.100.50.1".

**server_port**: The port of the server you are connecting to, for example, "1008".

**server_password**: The password of the server you are connecting to. Unless server operator set otherwise, it is default to be empty ("").

**server_no_check_certificate**: Change it to "true" if you don't want to verify the server's SSL/TLS certificate, **this is not recommended**!

**persistent_client_hash**: By default, EARCIS will generate a new client address hash everytime at launch, and you can generate a new one during runtime. If you want EARCIS to stick to one address hash at launch, you can set a qualified hash here (you will still be able to generate a new one at runtime). Client address hashes can be safely shared in insecure channels. Note: although setting a persistent hash improves convenience, it may reduce your anonymity. 

#####After finished editing the settings, you can launch EARCIS:
```sh
python client.py
```
Detailed instructions on runtime commands are displayed at launch.

How does it work?
----
EARCIS utilises AES Cipher in block mode CBC. 

When your message is entered into EARCIS, EARCIS will generate a unique random Initialisation Vector(IV) and encrypt the message with your secure key. The encrypted message, along with its original length and IV (which will not help an attacker) are sent to the relay server. SSL/TLS encryption between you and the server will add an extra layer of security in transit. The randomly hashed address of you and your recepient will also be sent.

The relay server then relays the message to the correct recepient according to the recepient address hash you have provided. It also tells the recepient who sent it (your address hash). The server ensures that the clients don't need to connect at real time to send messages. (Client address hashes can be safely shared in insecure channels.)

As the encryption and decryption processes are entirely done at client ends, the server (and anyone who attempts to wiretap it in transit) will **not** be able to tell the content of the message.

Note: To make regular message exchanges easier, the shared secure key you enter into ```client_settings.json``` **will be kept in clear text in your local file**, but you can always apply a new key with ```/key``` command.

License
----

EARCIS is licensed under The MIT License, you are free to modify and distribute it under restrictions defined by The MIT License. For full license details, see LICENSE.
