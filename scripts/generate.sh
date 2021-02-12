#!/bin/bash
cd /opt/woodCDN/cron
/usr/bin/python3 generate.py certs
/usr/bin/python3 generate.py nginx
