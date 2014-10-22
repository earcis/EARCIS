def serverip_match(serverip):
    from sys import exit
    import socket
    from re import match
    try:
        socket.inet_aton(serverip)
        servername = ""
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, serverip)
            servername = ""
        except socket.error:
            if not match("^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}$", serverip):
                print "Server IP/domain not in correct shape, please check config."
                exit(0)
                #if it is a real domain, just pass it along as serverip...

    print "Server IP/domain set as",serverip,"."
    return serverip

def serverport_match(serverport):
    if not (0 < serverport < 65536):
        print "Server port must be between 1-65535, please check config."
        exit(0)
    print "Server port set as",serverport,"."
    return serverport

def client_checkkey(clientkey):
    if (len(clientkey) > 64) or (len(clientkey) < 6) or (' ' in clientkey):
        return False
    else:
        return True

def serverpassword_match(serverpassword):
    from re import match
    if not (match("^[A-Za-z0-9_-]+$", serverpassword)):
        return False
    if len(serverpassword) > 32:
        return False
    return True
