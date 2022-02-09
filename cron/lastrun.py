#!/usr/bin/python3
import sys, time, socket
sys.path.append("..") # Adds higher directory to python modules path.
from Class.cli import CLI

cli = CLI()
hostname = socket.gethostname()
if "." in hostname:
    sub = hostname.split(".", 1)[0]
else:
    sub = hostname

while True:
    time.sleep(30)
    #Check if nginx is running / port 80 is reachable
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',80))
    if result != 0: continue
    status = cli.execute(["UPDATE pops SET lastrun = ? WHERE name = ?",int(time.time()),sub])
