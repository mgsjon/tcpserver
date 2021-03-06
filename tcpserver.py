#!/usr/bin/env python

import argparse
import socket
from handlers import square
from collections import Counter
from threading import Thread, Event, active_count
from time import time


config = {
    "host": "0.0.0.0",
    "port": 9999,
    "buffer": 4096,
    "timeout": 3,
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
        self.addr = addr
        self.socket = socket
        self._server_thread = server_thread
        self._dead = False
        self.daemon = True
        verbose("Connected: %s:%s" % addr)

    def run(self):

        self.socket.settimeout(config["timeout"])
        connection_start = time()

        while not self._server_thread.stopped:
            try:

                # Wait for input data from the socket
                data = self.socket.recv(config["buffer"])

                # Start processing client's request
                verbose("Request from %s:%s -> %s" % (self.addr + (data, )))
                cnt["req"] += 1

                if not data or data.rstrip() == "close":
                    verbose("Connection closed by request from %s:%s" % self.addr)
                    break

                # Call request handler
                response = config['handler'](data)

                # Send the response
                self.socket.send(response)
                verbose("Response to %s:%s -> %s" % (self.addr + (response, )))

            except socket.timeout:
                cnt["to"] += 1
                verbose("Connection closed due to a timeout on %s:%s" % self.addr)
                break
            except socket.error as e:
                if e[0] == 35:
                    continue
                self._dead = True
                verbose("Connection interrupted by %s:%s" % self.addr)

        cnt["conn_time"] += (time() - connection_start)

        self.socket.close()


class ServerThread(Thread):

    def __init__(self):
        super(ServerThread, self).__init__()
        self._stop = Event()
        self.daemon = True
        self.rejected = {}

    @property
    def stopped(self):
        return self._stop.isSet()

    def stop(self):
        self._stop.set()

    def run(self):
        while True:
            try:
                client_socket, addr = tcp_socket.accept()
                if addr in self.rejected:
                    del self.rejected[addr]
            except socket.error as e:
                addr_str = "%s:%s" % addr
                if addr not in self.rejected:
                    if e[0] == 24:
                        verbose("[!] Too many connections (%s+) at a time. Suspended connection request from %s\n" %
                                (active_count() - 1, addr_str))
                    else:
                        verbose("[!] Suspended connection request from %s\n" % addr_str)
                    self.rejected[addr] = True
                continue

            try:
                cnt["threads"] += 1
                client_thread = ClientThread(client_socket, addr, self)
                client_thread.start()
            except Exception as e:
                verbose("[!] Couldn't run thread for connection request from %s: %s\n" % (addr + (e, )))


if __name__ == "__main__":

    set_config()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    tcp_socket.bind((config["host"], config["port"]))
    tcp_socket.listen(5)

    server_start_time = time()

    print("Server started on %s:%s. Buffer size: %s bytes. Timeout: %s s. Verbose: %s." %
          (config["host"], config["port"], config["buffer"], config["timeout"], config["verbose"]))
    print("Press 'Ctrl+C' whenever you want to stop the server.\n")

    # Start sever thread
    server_thread = ServerThread()
    cnt["threads"] += 1
    server_thread.start()

    while True:
        try:
            # Wait for Ctrl+C to stop server
            exit_signal = raw_input("")
        except KeyboardInterrupt:
            server_thread.stop()
            break

    server_end_time = time()

    print("Server stopped\n")

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
        Threads: %s
    """ % (total_time, cnt["conn"], cnt["req"], req_per_conn, conn_time, cnt["to"], cnt["threads"])

    print(stats)
