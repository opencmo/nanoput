#!/opt/enr/virtupy/bin/python
# $Id$
import operator
import gzip
import sys
import os
import subprocess
import struct
import time
import datetime
import calendar
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from common import *
import redis
from dateutil.parser import parse

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

camps = {
    '283':['1735','1736','1737','1754','1755','1756','1757','1758','1759'],
    '284':['1738','1739','1740','1760','1761','1762','1763','1764','1765'],
    '285':['1741','1742','1743','1766','1767','1768','1769','1770','1771'],
    '286':['1744','1745','1746','1772','1773','1774','1775','1776','1777']
}

to_camps = {
    '1735':'283','1736':'283','1737':'283','1754':'283','1755':'283','1756':'283','1757':'283','1758':'283','1759':'283',
    '1738':'284','1739':'284','1740':'284','1760':'284','1761':'284','1762':'284','1763':'284','1764':'284','1765':'284',
    '1741':'285','1742':'285','1743':'285','1766':'285','1767':'285','1768':'285','1769':'285','1770':'285','1771':'285',
    '1744':'286','1745':'286','1746':'286','1772':'286','1773':'286','1774':'286','1775':'286','1776':'286','1777':'286'
}
r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

f = open('/ebs3/boba/wins_moto.txt','r')
lines = f.readlines()

imp = dict()
spend = dict()
    
for line in lines:
    line = line.strip()
    line = line.split("\t")
    price = float(line[1])
    user = line[2]
    ts = line[0]
    camp = to_camps[ts]
    ts_key = "ab_test2_ts_%s_T" % (ts)
    c_key = "ab_test2_c_%s_T" % (camp)
    if r.zrank(ts_key, user) is not None:
        if ts not in imp:
            imp[ts] = 1
        else: 
            imp[ts] += 1
        if ts not in spend:
            spend[ts] = price
        else:
            spend[ts] += price

    if r.zrank(c_key, user) is not None:
        if camp not in imp:
            imp[camp] = 1
        else: 
            imp[camp] += 1
        if camp not in spend:
            spend[camp] = price
        else:
            spend[camp] += price

print imp
print spend


