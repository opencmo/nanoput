import redis
import base64
import sys
import struct
import time
import glob
import os
import gzip
from datetime import timedelta, date

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

to_camps = {
    '1735':'283','1736':'283','1737':'283','1754':'283','1755':'283','1756':'283','1757':'283','1758':'283','1759':'283',
    '1738':'284','1739':'284','1740':'284','1760':'284','1761':'284','1762':'284','1763':'284','1764':'284','1765':'284',
    '1741':'285','1742':'285','1743':'285','1766':'285','1767':'285','1768':'285','1769':'285','1770':'285','1771':'285',
    '1744':'286','1745':'286','1746':'286','1772':'286','1773':'286','1774':'286','1775':'286','1776':'286','1777':'286',
    '1785':'294','1786':'294','1787':'294','1788':'294','1789':'295','1790':'295','1791':'295','1792':'295','1793':'295',
    '1794':'295','1795':'295','1796':'295','1797':'295','1798':'295','1747':'287','1748':'287','1749':'287','1781':'289',
    '1784':'289','1799':'289','1800':'289','1804':'289','1808':'289','1809':'305','1815':'305','1810':'306','1811':'307'
}

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def is_user_suspicious(modUid):
    l1 = int(modUid[:8],16)& 0xffffffff
    l2 = int(modUid[8:16],16) & 0xffffffff
    l3 = int(modUid[16:24],16) & 0xffffffff
    l4 = int(modUid[24:],16) & 0xffffffff
    s = struct.pack("<IIII", l1, l2, l3, l4)
    buid = base64.b64encode(s)
    return (('+' in buid) or ('/' in buid))

def parse_date(datestring):
    return date(int(datestring[:4]), int(datestring[4:6]), int(datestring[6:8]))

def read_file(fname):
    g = gzip.GzipFile(fname)
    lines = g.readlines()
    line_cnt = 0
    for line in lines:
        line_cnt +=1
        line = line.strip()
        line = line.split("\t")
        user = line[4]
        if is_user_suspicious(user):
            continue
        uts = long(line[1])
        type = line[5]
        if type == "C":
            c = line[6]
            c_status = line[7]
            c_redis_key = "ab_test2_c_%s_%s" % (c, c_status)
            c_T_redis_key = "ab_test2_c_%s_T" % (c)
            c_C_redis_key = "ab_test2_c_%s_C" % (c)
            c_N_redis_key = "ab_test2_c_%s_N" % (c)
            c_dirty_redis_key = "dirty_ab_test2_c_%s" % (c)
            if r.zrank(c_T_redis_key, user) is not None and c_status != "T":
                r.zrem(c_T_redis_key, user)
                r.zadd(c_dirty_redis_key, uts, user)
            elif r.zrank(c_C_redis_key, user) is not None and c_status != "C":
                r.zrem(c_C_redis_key, user)
                r.zadd(c_dirty_redis_key, uts, user)
            elif r.zrank(c_N_redis_key, user) is not None and c_status != "N":
                r.zrem(c_N_redis_key, user)
                r.zadd(c_dirty_redis_key, uts, user)
            elif r.zrank(c_dirty_redis_key, user) is None:
                r.zadd(c_redis_key, uts, user)
        elif type == "TS":   
            ts = line[6]
            ts_status = line[7]
            ts_redis_key = "ab_test2_ts_%s_%s" % (ts, ts_status)
            ts_T_redis_key = "ab_test2_ts_%s_T" % (ts)
            ts_C_redis_key = "ab_test2_ts_%s_C" % (ts)
            ts_dirty_redis_key = "dirty_ab_test2_ts_%s" % (ts)
            c_dirty_redis_key = "dirty_ab_test2_c_%s" % (to_camps[ts])
            if r.zrank(c_dirty_redis_key, user) is not None:
                r.zrem(ts_T_redis_key, user)
                r.zrem(ts_C_redis_key, user)
                r.zadd(ts_dirty_redis_key, uts, user)
            elif r.zrank(ts_T_redis_key, user) is not None and ts_status != "T":
                r.zrem(ts_T_redis_key, user)
                r.zadd(ts_dirty_redis_key, uts, user)
            elif r.zrank(ts_C_redis_key, user) is not None and ts_status != "C":
                r.zrem(ts_C_redis_key, user)
                r.zadd(ts_dirty_redis_key, uts, user)
            elif r.zrank(ts_dirty_redis_key, user) is None:
                r.zadd(ts_redis_key, uts, user)
               
    return line_cnt

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Start and End dates in YYYYMMDD format required"
    else:
        start_date = parse_date(str(sys.argv[1]))
        end_date = parse_date((sys.argv[2]))
        for current_date in daterange(start_date, end_date):
            year = current_date.year
            month = current_date.month
            day = current_date.day
            if day < 10:
                day = "0%s" % day
            if month < 10:
                month = "0%s" % month
            day_prefix = "/opt/enr/log/processing/year=%s_month=%s_day=%s" % (year, month, day)
            for hour in range(0,24):
                if hour < 10:
                    hour = "0%s" % hour
                file_prefix = "%s_hour=%s_type=abtestassignment*" % (day_prefix, hour)
                print "Loading %s %s" % (current_date.strftime("%Y-%m-%d"), hour)
                for filename in glob.glob(file_prefix):
                    print "Read lines %s" % read_file(filename)
