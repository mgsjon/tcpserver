#!/usr/bin/env python

import argparse
import socket


DEFAULT_CONFIG = {
    'host': '0.0.0.0',
    'port': 9999,
    'buffer': 4096
}


def get_config():
    result = DEFAULT_CONFIG.copy()
    parser = argparse.ArgumentParser(prog='tcpserver')
    parser.add_argument('--h', dest='host', type=str, help="Host")
    parser.add_argument('--p', dest='port', type=int, help="Port")
    parser.add_argument('--b', dest='buffer', type=int, help="Buffer size in bytes")
    args = parser.parse_args()
    user_config = vars(args)
    result.update((k, v) for k, v in user_config.iteritems() if v is not None)
    return result


def response(n):
    try:
        n = int(n)
        return "Got %s. My response is %s.\n" % (n, n ** 2)
    except ValueError:
        return "Sorry, I accept numbers only.\n"

if __name__ == '__main__':
    config = get_config()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #socket.SOMAXCONN

    tcp_socket.bind((config['host'], config['port']))
    tcp_socket.listen(5)
    print "Server is ready."

    client_socket, addr = tcp_socket.accept()
    print "Connected: %s:%s" % addr

    while True:
        data = client_socket.recv(config['buffer'])
        if not data:
            break

        client_socket.send(response(data))
        if data.rstrip() == "close":
            break

    print "Server stopped"
