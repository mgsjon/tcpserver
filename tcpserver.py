#!/usr/bin/env python

import argparse
import socket
from handlers import square
from collections import Counter
from threading import Thread

config = {
    "host": "0.0.0.0",
    "port": 9999,
    "buffer": 4096,
    "timeout": 15,
    "verbose": False,
    "handler": square
}

cnt = Counter()


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


class ClientThread(Thread):

    def __init__(self, socket, addr):
        super(ClientThread, self).__init__()
        cnt['conn'] += 1
        self.ip = addr[0]
        self.port = addr[1]
        self.socket = socket
        verbose("Connected: %s:%s" % addr)

    def run(self):

        self.socket.settimeout(config["timeout"])
        self.socket.send("Hi! Send you request or 'close' to close connection.\r\n")

        while True:
            try:
                data = self.socket.recv(config["buffer"])
                cnt['req'] += 1  # Let's count 'close' requests too
                if not data or data.rstrip() == "close":
                    break
                self.socket.send(square(data))
            except socket.timeout:
                self.socket.send("I have to close the connection due to timeout. Sorry!\r\n")
                break

        self.socket.send("Bye-bye!\r\n")
        self.socket.close()

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
        client_thread = ClientThread(client_socket, addr)
        client_thread.start()

    #verbose("Server stopped")
