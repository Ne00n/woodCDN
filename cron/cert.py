#!/usr/bin/python3
import time, sys
sys.path.append("..") # Adds higher directory to python modules path.
from Class.cert import Cert

cert = Cert()

while True:
    cert.renew()
    time.sleep(300)
