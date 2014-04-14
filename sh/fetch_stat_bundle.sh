#!/bin/sh
cd /opt/enr
status=`/usr/bin/git status -s`
if [ "$status" != "" ]; then
   echo Something modified here, aborting.
   exit 1
fi
/usr/bin/git pull -u 
# /opt/enr/virtupy/bin/python /opt/enr/py/fetch_stat_bundle.py  2>&1 >> /opt/enr/log/fetch_stat_bundle.log