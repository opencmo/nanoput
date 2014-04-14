import traceback
import sys
import os
import time
import datetime

import pg8000
import boto
from common import *

# Defaults

db_user = 'enr'
db_pass = 'Kapuestra2'

# Globals

dbCon = None


def create_cluster(rsCon, cluster_id):
    create_resp = rsCon.create_cluster(cluster_identifier=cluster_id,
                              node_type='dw.hs1.xlarge',
                              master_username=db_user,
                              master_user_password=db_pass,
                              db_name='db0',
                              cluster_type='multi-node',
                              number_of_nodes=2)
    return create_resp

def wait_for_cluster(rsCon, cluster_id):
    while True:
        r = rsCon.describe_clusters(cluster_id)
        resp = r['DescribeClustersResponse']
        res = resp['DescribeClustersResult']
        clusters = res['Clusters']
        # We assume there's only one since we supplied ID
        cluster = clusters[0]
        status = cluster['ClusterStatus']
        print 'Waiting for cluster to become available; current status: %s' % status
        if status != u'creating':
            break
        time.sleep(5)
    return r

tbl = """
CREATE TABLE ado_ucsess (
    ssid VARCHAR(64),
    fsid VARCHAR(64),
    stats_version VARCHAR(64),
    bidder_version VARCHAR(64),
    logic_version VARCHAR(64),
    content_version VARCHAR(64),
    server_ts VARCHAR(64),
    dt VARCHAR(64),
    hour VARCHAR(2),
    http_code VARCHAR(4),
    unit_id VARCHAR(64),
    stat_id VARCHAR(64),
    bid FLOAT4,
    remote_addr VARCHAR(32),
    uuid VARCHAR(64),
    uuid_generated VARCHAR(1),
    accept_lang VARCHAR(64),
    browser VARCHAR(64),
    browser_version VARCHAR(64),
    os_name VARCHAR(64),
    os_version VARCHAR(64),
    flash_version VARCHAR(64),
    country_id INT4,
    region_id INT4,
    state_id INT4,
    city_id INT4,
    postal_code_id INT4,
    area_code_id INT4,
    time_zone INT4,
    latitude INT4,
    longitude INT4,
    dma_id INT4,
    msa_id INT4,
    connection_type_id INT4,
    line_speed_id INT4,
    ip_routing_type_id INT4,
    asn_id INT4,
    sld_id INT4,
    tld_id INT4,
    organization_id INT4,
    carrier_id INT4,
    request_method VARCHAR(32),
    pub_req_id VARCHAR(32),
    mid VARCHAR(64),
    rtb INT2,
    vast INT2,
    vpaid INT2,
    http_ref VARCHAR(1024),
    ref_domain VARCHAR(128),
    ad_types VARCHAR(64),
    platform VARCHAR(64),
    categories VARCHAR(128),
    block_cat VARCHAR(128),
    bid_floor FLOAT4,
    bid_floor_base INT4,
    user_interaction VARCHAR(64),
    companion_size VARCHAR(64),
    timeout INT4,
    bitrate VARCHAR(64),
    duration INT4,
    media_types VARCHAR(128),
    vid VARCHAR(128),
    tags VARCHAR(512),
    title VARCHAR(64),
    descr VARCHAR (64),
    vid_url VARCHAR(64),
    x1 VARCHAR(4),
    query_string VARCHAR(1024),
    headers VARCHAR(1024),
    proxies VARCHAR(64),
    cookies VARCHAR(128),
    ua VARCHAR(128),
    accept_list VARCHAR(128),
    user_data VARCHAR(128),
    context VARCHAR(256),
    request_body VARCHAR(256),
    x2 VARCHAR(4),
    taxonomy VARCHAR(64),
    targeted_taxonomy VARCHAR(64),
    x3 VARCHAR(4)
)
    SORTKEY(server_ts)
"""

# TODO come up with enums

def exec_sql(cursor, sql):
    log("Executing %s" % sql)
    cursor.execute(sql)
    log("")
    for row in cursor:
        log("\t%s" % row)
    log("")    

def connect_to_db(endpoint):
    """
    @param r: Response from describe_clusters
    
    """
    global dbCon
    log("Connecting to DB at endpoint %s" % endpoint)
    host = str(endpoint['Address'])
    port = int(endpoint['Port'])
    # u'Endpoint': {u'Port': 5439, u'Address': u'enr-cluster-2.cp4j2qq4oe4h.us-east-1.redshift.amazonaws.com'},
    dbCon = pg8000.DBAPI.connect(host=host, port=port, user=db_user, password=db_pass)
    log("Success!")
    return dbCon

def close(dbCon):
    if not dbCon:
        return
    try:
        dbCon.close()
    except Excception, e:
        log(dbCon)

def exec_sql(dbCon, sql):
    cur = dbCon.cursor()
    try:
        retval = cur.execute(tbl)
        if retval:
            log(retval)
    except pg8000.errors.ProgrammingError, e:
        try:
            cur.execute("SELECT * FROM stl_load_errors")
            retval = cur.fetchall()
            log("Error: %s" % e)
            log(str(retval))
        except Exception, e2:
            raise e
            

def load_data():
    endpoint = {u'Port': 5439, u'Address': u'enr-cluster-2.cp4j2qq4oe4h.us-east-1.redshift.amazonaws.com'}
    connect_to_db(endpoint)
    cur = dbCon.cursor()
    log ("Creating table...")
    exec_sql(dbCon,tbl)
    cp_cmd = """
       COPY ado_ucsess FROM 
       's3://unitcore-stats3/grisha'
       CREDENTIALS 
       'aws_access_key_id=%(akey)s;aws_secret_access_key=%(skey)s'
       delimiter '\t' gzip
       """ % CREDS
    exec_sql(dbCon,cp_cmd)
    log("Ok")

def main():
    load_data()
    sys.exit()

    cluster_id = 'enr-cluster-2'
    rsCon = boto.connect_redshift(CREDS['akey'], CREDS['skey'])
    create_cluster(rsCon, cluster_id)
                         
    try:
        r = wait_for_cluster(rsCon, cluster_id)
        endpoint = r['DescribeClustersResponse']['DescribeClustersResult']['Clusters'][0]['Endpoint']
        log("Cluster ready: %s" % r)
        connect_to_db(endpoint)
        cur = dbCon.cursor()
        log ("Creating table...")
        retval = cur.execute(tbl)
        if retval:
            log(retval)
        retval = cur.fetchall()
        if retval:
            log(retval)
        cp_cmd = """
       COPY ado_ucsess FROM 
       's3://unitcore-stats3/year=2013/month=07/day=31/hour=14/type=sessions/' 
       CREDENTIALS 
       'aws_access_key_id=%(akey)s;aws_secret_access_key=%(skey)s'
       delimiter '\t' gzip
       """ % d
        # create table testtable (testcol int);
    except Exception, e:
        traceback.print_exc()
    finally:
        time.sleep(3)
        close(dbCon)
  #      rsCon.delete_cluster(cluster_id, True)

if __name__ == "__main__":
    main()


