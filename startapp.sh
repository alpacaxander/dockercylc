#!/bin/sh
export HOME=/root
cylc run helloworld
#nohup python /cylctest/WebBasedCylc/manage.py runserver "0.0.0.0:8000"
exec cylc gui helloworld