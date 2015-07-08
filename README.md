# tcpserver

A simple TCP server written on Python. Requires Python 2.7.

### Run server

```
$ python tcpserver/tcpserver.py -h
usage: tcpserver [-h] [--h HOST] [--p PORT] [--b BUFFER] [--t TIMEOUT] [-v]

optional arguments:
  -h, --help   show this help message and exit
  --h HOST     Host
  --p PORT     Port
  --b BUFFER   Buffer size in bytes
  --t TIMEOUT  Max. timeout in seconds
  -v           Output messages on connections activity
```