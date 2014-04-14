import redis
import base64
import struct
import time

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

to_camps = {
    '1735':'283','1736':'283','1737':'283','1754':'283','1755':'283','1756':'283','1757':'283','1758':'283','1759':'283',
    '1738':'284','1739':'284','1740':'284','1760':'284','1761':'284','1762':'284','1763':'284','1764':'284','1765':'284',
    '1741':'285','1742':'285','1743':'285','1766':'285','1767':'285','1768':'285','1769':'285','1770':'285','1771':'285',
    '1744':'286','1745':'286','1746':'286','1772':'286','1773':'286','1774':'286','1775':'286','1776':'286','1777':'286',
    '1785':'294','1786':'294','1787':'294','1788':'294','1789':'295','1790':'295','1791':'295','1792':'295','1793':'295',
    '1794':'295','1795':'295','1796':'295','1797':'295','1798':'295'
}

def m2c(modUid):
    l1 = int(modUid[:8],16)& 0xffffffff
    l2 = int(modUid[8:16],16) & 0xffffffff
    l3 = int(modUid[16:24],16) & 0xffffffff
    l4 = int(modUid[24:],16) & 0xffffffff
    s = struct.pack("<IIII", l1, l2, l3, l4)
    return base64.b64encode(s)
    
uts = int(round(time.time() * 1000))

c_keys = r.keys("ab_test2_c_*")
c_list = sorted(set([c_key.split("_")[3] for c_key in c_keys]))
for c in c_list:
    for s in ['T','C']:
        key = "ab_test2_c_%s_%s" % (c, s)
        key_n = "ab_test2_c_%s_N" % (c)
        users = set(r.zrange(key, 0, -1))
        for user in users:
            buid = m2c(user)
            if ('+' in buid) or ('/' in buid):
                r.zrem(key, user)
                r.zadd(key_n, uts, user)

ts_keys = r.keys("ab_test2_ts_*")
ts_list = sorted(set([ts_key.split("_")[3] for ts_key in ts_keys]))
for ts in ts_list:
    for s in ['T','C']:
        key = "ab_test2_ts_%s_%s" % (ts, s)
        key_n = "ab_test2_ts_%s_N" % (ts)
        users = set(r.zrange(key, 0, -1))
        for user in users:
            buid = m2c(user)
            if ('+' in buid) or ('/' in buid):
                r.zrem(key, user)
                r.zadd(key_n, uts, user)

