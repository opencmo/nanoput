#!/opt/enr/virtupy/bin/python
# $Id$
import redis

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

# for segment in ['archived:segment:362:fp:220', 'archived:segment:363:fp:220', 'archived:segment:364:fp:220', 'archived:segment:365:fp:220', 'archived:segment:366:fp:220']:
#     print "Segment %s total count: %s" % (segment, r.zcard(segment))
# 
# #c_keys = r.keys("ab_test2_c_*")
# #c_list = sorted(set([c_key.split("_")[3] for c_key in c_keys]))
# c_list = sorted(set(['283','284','285','286','287']))
# 
# for segment in ['archived:segment:362:fp:220', 'archived:segment:363:fp:220', 'archived:segment:364:fp:220', 'archived:segment:365:fp:220', 'archived:segment:366:fp:220']:
#     for c in c_list:
#         for s in ['T','C']:
#             zkey = "tmp_ab_test2_%s_int_c_%s_%s" % (segment, c, s)
#             expset = "ab_test2_c_%s_%s" % (c, s)
#             print "Size of %s for campaign %s: %s" % (s, c, r.zcard(expset))
#             res = r.zinterstore(zkey, [segment, expset])
#             r.delete(zkey)
#             if res:
#                 print "Intersection of segment %s and %s for campaign %s: %s" % (segment, s, c, res)
#         print '----------------------'
# print 
# print '==========================='
# 
#ts_keys = r.keys("ab_test2_ts_*")
#ts_list = sorted(set([ts_key.split("_")[3] for ts_key in ts_keys]))
ts_list = sorted(set(['1931','1932','1933','1934','1936','1937', '1938', '1939']))

for ts in ts_list:
    for s in ['T','C']:
        expset = "ab_test2_ts_%s_%s" % (ts, s)
        print "Size of %s for TS %s: %s" % (s, ts, r.zcard(expset))
    print '----------------------'
