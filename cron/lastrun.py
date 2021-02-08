#!/usr/bin/python3
import sys, time, socket
sys.path.append("..") # Adds higher directory to python modules path.
from Class.cli import CLI

cli = CLI()
hostname = socket.gethostname()

status = cli.execute(["UPDATE pops SET lastrun = ? WHERE name = ?",int(time.time()),hostname])
time.sleep(30)
status = cli.execute(["UPDATE pops SET lastrun = ? WHERE name = ?",int(time.time()),hostname])
