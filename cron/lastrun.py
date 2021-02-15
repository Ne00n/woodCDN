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
    status = cli.execute(["UPDATE pops SET lastrun = ? WHERE name = ?",int(time.time()),sub])
    time.sleep(30)
