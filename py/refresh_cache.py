from common import *
import redis
from db import EnrDb
from MySQLdb.cursors import DictCursor

REDIS_HOST = 'redis-host'
REDIS_PORT =  6379


def main():
    db = EnrDb()
    db.connect(cursorclass=DictCursor) 
    sql = """
         SELECT bannerid, 
                description, 
                views quantity,
                target_impression daily_quantity,
                revenue cpm, 
                htmltemplate body, 
                width, height, 
                compiledlimitation targeting,
                keyword
         FROM 
                revive.rv_banners b 
         JOIN 
                revive.rv_campaigns c ON b.campaignid = c.campaignid
         WHERE 
                CURRENT_TIMESTAMP BETWEEN activate_time AND IFNULL(expire_time, '2038-01-01')
         """
    stuff = db.runSql(sql)
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    for banner in stuff:
        targeting = banner['targeting']
        ad_id = banner['bannerid']
        # all_ads Set has the IDs of ads to serve
        targeting = banner['targeting']
        targeting = targeting.strip()
        print '<%s>' % targeting
        if targeting:
            eval(targeting)

        # Check if this one has been delivered
        quantity = banner['quantity']
        served = r.hget(ad_id, 'served')
        if served and served > quantity:
            print "Skipping %s: served %s>%s" % (ad_id, served, quantity)
        else:
            r.sadd('all_ads', ad_id)        
            r.hmset(ad_id, banner)
            

def MAX_checkClient_Os(l_s, op):
    l = l_s.split(',')
    print l
    if op != '=~':
        raise Exception("Unknown op %s" % op)        
    return Targeting(l)
            
def MAX_checkGeo_Latlong(l_s, op):
    t = (lat_min, lat_max, long_min, long_max) = l_s.split(',')
    if op != '==':
        raise Exception("Unknown op %s" % op)
    return Targeting(t)


class Targeting(list):
    def __init__(self, l):
        list.__init__(self, l)

    def __and__(self, t2):
        return ['and', self, t2]

    def __or__(self, t2):
        return ['or', self, t2]
        

if __name__ == "__main__":
    main()
