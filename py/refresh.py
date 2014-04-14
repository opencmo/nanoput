# $Id$
import sys
import os
import time
import datetime
import urllib2

from common import *
from db import * 
from boto.ec2.elb import ELBConnection 

import hgapi

repo = hgapi.Repo(ENR_HOME)

# CONF_DIR

def write_logdef(f, prefix, tbl, cols):
    """
    log_format ado_s4 '"$time_iso8601","$remote_addr","$request_time","$enr_browser","$enr_os","$enr_device","$arg_srv","$arg_evt","$arg_pid","$arg_psite","$arg_ipid","$arg_crid","$arg_chid","$arg_e9mdi","$arg_e9as","$arg_ref","$arg_ssid","$arg_fsid","$cookie_ado_wid","$geoip_city_country_code","$geoip_city","$geoip_region",$geoip_postal_code","$geoip_dma_code","$geoip_area_code","$geoip_latitude","$geoip_longitude","$http_referer","$http_user_agent"';
    """
    f.write("log_format %s_%s " % (prefix, tbl))
    quoted_cols = ['"$%s"' % c for c in cols]
    f.write("'")
    f.write(",".join(quoted_cols))
    f.write("';")
    f.write("\n\n")
    f.flush()

def write_location(f, prefix, tbl):
    """
    location /ado/s4/ {
    log_not_found off;
    root   /opt/enr/a/htdocs;
    access_log  /opt/enr/log/ado.s4.enr.log ado_s4;
    
    expires -1;
    
    #	    if ($arg_event = "vpaid") {
    #	       rewrite ^ /1x1_302.gif redirect;
    #	    }
    rewrite ^ /1x1.gif break;
    }
    
    """
    f.write("location /%s/%s/ {\n" % (prefix, tbl))
    f.write("    log_not_found off;\n")
    f.write("    root /opt/enr/a/htdocs;\n");
    f.write("    access_log /opt/enr/log/%s.%s.enr.log %s_%s;\n" % (prefix,tbl, prefix,tbl))
    f.write("    expires -1;\n");
    f.write("    rewrite ^ /1x1.gif break;\n");
    f.write("}\n");
    f.write("\n");
    f.flush()
    

def get_cols_info(db):
    retval = db.getColsInfo()
    return retval
    
def write_conf_files(db):
    log("Getting columns info...")
    cols_info = get_cols_info(db)
    logdefs_fname = os.path.join(CONF_DIR, 'logdefs1.conf')
    logdefs_f = open(logdefs_fname, 'w')
    locations_fname = os.path.join(CONF_DIR, 'locations1.conf')
    locations_f = open(locations_fname, 'w')
    user_cnt = 0
    tbl_cnt = 0
    info = ""
    for user in cols_info:
        log('Processing for %s' % user)
        if not validate_enr_ident(user):
                # Last line of defense -- 
                # we don't want a bad identifier in one definition to screw up 
                # others...
                log("Bad user prefix %s, skipping"  % user)
                info += "Bad prefix %s;\n" % user
                continue
        user_cnt += 1        
        tbls = cols_info[user]
        for tbl in tbls:
            if not validate_enr_ident(tbl):
                # Last line of defense -- 
                # we don't want a bad identifier in one definition to screw up 
                # others...
                log("Bad table name %s for %s, skipping" % (tbl, user))
                info += "Bad table name %s.%s;\n" % (user,tbl)
                continue
            tbl_cnt += 1
            log("\tProcessing table %s" % tbl)
            cols = tbls[tbl]
            cols_ok = True
            for col in cols:
                # Last line of defense -- 
                # we don't want a bad identifier in one definition to screw up 
                # others...
                if not validate_enr_colname(col):
                    log("Bad column name %s in %s.%s, will ignore %s" % (col,user,tbl,tbl))
                    info += "Bad column %s.%s.%s;\n" % (user,tbl,col)
                    cols_ok = False
                    break
            if cols_ok:
                write_logdef(logdefs_f, user, tbl, cols)
                write_location(locations_f, user, tbl)
                info += "%s.%s OK!\n" % (user,tbl)
    logdefs_f.close()
    log("Wrote %s" % logdefs_fname)
    locations_f.close()
    log("Wrote %s" % locations_fname)
    log ("Processed total of %s tables for %s users" % (tbl_cnt, user_cnt))
    return ([logdefs_fname, locations_fname], info)

def query_node(host, path):
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    top_url = "http://%s/manage" % host
    password_mgr.add_password(None, top_url, CREDS['http_user'], CREDS['http_passwd'])
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    url = "%s%s" % (top_url, path)
    response = opener.open(url)
    result = response.read()
    return result

def get_cur_rev(host):
    """
    Get current revision of code at host

    """
    return query_node(host, '/hg/rev')

def update(host):
    """
    Get current revision of code at host

    """
    return query_node(host, '/hg/update')

def reload(host):
    """
    Get current revision of code at host

    """
    return query_node(host, '/hg/reload')

def refresh_nodes():
    regions_to_nodes = list_node_ids()
    id_to_dns = {}
    for region in regions_to_nodes:
        ec2_con = boto.ec2.connect_to_region(region, 
                                             aws_access_key_id=CREDS['akey'], 
                                             aws_secret_access_key=CREDS['skey'])
        reservations = ec2_con.get_all_instances(regions_to_nodes[region])
        for res in reservations:
            for inst in res.instances:
                id_to_dns[inst.id] = inst.dns_name
    fail = {}
    success = []
    tot_cnt = upd_cnt = fail_cnt = 0
    for inst_id in id_to_dns:
        tot_cnt += 1
        try:
            inst_host = id_to_dns[inst_id]
            log("Contacting %s: (%s):" % (inst_id, inst_host))
            cur_rev = get_cur_rev(inst_host)
            log("Current revision: %s" % cur_rev)
            log("Updating...")
            msg = update(inst_host)
            log(msg)
            log("Reloading...")
            msg = reload(inst_host)
            log(msg)
            upd_cnt += 1
        except Exception,e:
            fail_cnt += 1
            log("Error updating host %s (%s): %s" % (inst_id, inst_host, e))
    log("Processed %s instances, updated %s, failed to updated %s" % (tot_cnt, upd_cnt, fail_cnt))

def main():
    db = EnrDb()
    print "Connecting..."
    db.connect()

    (conf_files, msg) = write_conf_files(db)
    log ("Committing %s" % conf_files)
    commit_result =  repo.hg_commit(msg, files = conf_files)
    log(commit_result)

    refresh_nodes()

if __name__ == "__main__":
    log("Refreshing...")
    main()
    log("Done")
        


