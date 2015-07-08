#!/usr/bin/env python

import argparse
import socket
from handlers import square
from collections import Counter
from threading import Thread, Event
from time import time

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
    parser.add_argument("--t", dest="timeout", type=int, help="Max. timeout in seconds")
    parser.add_argument("-v", dest="verbose", action="count", help="Output messages on server activity")
    args = parser.parse_args()
    user_config = vars(args)
    config.update((k, v) for k, v in user_config.items() if v is not None)


def verbose(msg):
    if config["verbose"]:
        print(msg)


class ClientThread(Thread):

    def __init__(self, socket, addr, server_thread):
        super(ClientThread, self).__init__()
        cnt["conn"] += 1
        self.ip = addr[0]
        self.port = addr[1]
        self.socket = socket
        self._server_thread = server_thread
        self.daemon = True
        verbose("Connected: %s:%s" % addr)

    def run(self):

        self.socket.settimeout(config["timeout"])
        self.socket.send("Hi! Send you request or 'close' to close connection.\n")
        connection_start = time()

        while not self._server_thread.stopped:
            try:
                data = self.socket.recv(config["buffer"])
                cnt["req"] += 1  # Count 'close' requests too
                if not data or data.rstrip() == "close":
                    break
                self.socket.send(square(data))
                verbose("Response to %s:%s" % (self.ip, self.port))
            except socket.timeout:
                cnt["to"] += 1
                self.socket.send("I have to close the connection due to timeout. Sorry!\n")
                verbose("Connection timeout on %s:%s" % (self.ip, self.port))
                break

        cnt["conn_time"] += (time() - connection_start)
        self.socket.send("Bye-bye!\n")
        self.socket.close()


class ServerThread(Thread):

    def __init__(self):
        super(ServerThread, self).__init__()
        self._stop = Event()
        self.daemon = True

    @property
    def stopped(self):
        return self._stop.isSet()

    def stop(self):
        self._stop.set()

    def run(self):
        while True:
            client_socket, addr = tcp_socket.accept()
            cnt["threads"] += 1
            client_thread = ClientThread(client_socket, addr, self)
            client_thread.start()


if __name__ == "__main__":

    set_config()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    tcp_socket.bind((config["host"], config["port"]))
    tcp_socket.listen(5)

    server_start_time = time()

    print("Server started on %s:%s. Press 'Ctrl+C' whenever you want to stop it.\n" % (config["host"], config["port"]))

    server_thread = ServerThread()
    cnt["threads"] += 1
    server_thread.start()

    while True:
        try:
            exit_signal = raw_input("")
        except KeyboardInterrupt:
            server_thread.stop()
            break

    server_end_time = time()

    print("\nServer stopped")

    if cnt["conn"]:
        req_per_conn = "%.4s" % (cnt["req"] / float(cnt["conn"]))
        conn_time = "%.4s s" % (cnt["conn_time"] / float(cnt["conn"]))
    else:
        req_per_conn = conn_time = "-"

    total_time = server_end_time - server_start_time

    stats = """
        Total execution time: %.2f s
        Connections: %s
        Requests: %s
        Avg. requests per connection: %s
        Avg. connection time: %s
        Timeouts: %s
    """ % (total_time, cnt["conn"], cnt["req"], req_per_conn, conn_time, cnt["to"])

    print(stats)
