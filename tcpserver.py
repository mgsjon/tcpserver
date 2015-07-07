#!/usr/bin/env python

import argparse
import socket
from handlers import square


config = {
    "host": "0.0.0.0",
    "port": 9999,
    "buffer": 4096,
    "timeout": 15,
    "verbose": False,
    "handler": square
}


def set_config():
    parser = argparse.ArgumentParser(prog="tcpserver")
    parser.add_argument("--h", dest="host", type=str, help="Host")
    parser.add_argument("--p", dest="port", type=int, help="Port")
    parser.add_argument("--b", dest="buffer", type=int, help="Buffer size in bytes")
    parser.add_argument("--v", dest="verbose", action="count", help="Output messages on server activity")
    args = parser.parse_args()
    user_config = vars(args)
    config.update((k, v) for k, v in user_config.items() if v is not None)


def verbose(msg):
    if config["verbose"]:
        print(msg)


if __name__ == "__main__":

    set_config()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #socket.SOMAXCONN

    tcp_socket.bind((config["host"], config["port"]))
    tcp_socket.listen(5)

    verbose("Server started.")

    while True:

        client_socket, addr = tcp_socket.accept()
        verbose("Connected: %s:%s" % addr)
        client_socket.settimeout(config["timeout"])
        client_socket.send("Hi! Send you request or 'close' to close connection.\r\n")

        while True:
            try:
                data = client_socket.recv(config["buffer"])
                if not data or data.rstrip() == "close":
                    break
                client_socket.send(square(data))
            except socket.timeout:
                client_socket.send("I have to close the connection due to timeout. Sorry!\r\n")
                break

        client_socket.send("Bye-bye!\r\n")
        client_socket.close()

    verbose("Server stopped")
