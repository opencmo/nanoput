from copy import deepcopy

import MySQLdb

from common import *

class EnrDb(object):
    def __init__(self):
        d = parse_creds(CRED_FILE)
        self.host = d['mysql_host']
        self.db = d['mysql_db']
        self.user = d['mysql_user']
        self.passwd = d['mysql_passwd']
        self.con = None
        
    def connect(self, **kwargs):
        self.con = MySQLdb.connect(host=self.host,
                                   db=self.db,
                                   user=self.user,
                                   passwd=self.passwd,
                                   **kwargs)
        return self.con

    def runSql(self, sql):
        cur = self.con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows

    def getLogdefs(self):
        sql = """
              SELECT ld.name, c.name, c.client_id, ld.data_collection_id, 
              GROUP_CONCAT(CONCAT_WS( '', '$', REPLACE(IF(code='','arg_placeholder',IFNULL(code,'arg_placeholder')), ' ','_')) ORDER BY lda.order_index, lda.code SEPARATOR '\\\\t') 
              FROM ld_data_collection ld
              LEFT JOIN ld_data_collection_attribute lda
              ON lda.data_collection_id = ld.data_collection_id
              JOIN ld_client c ON ld.client_id = c.client_id
              GROUP BY c.name, c.client_id, ld.name, ld.data_collection_id
              ORDER BY lda.order_index, lda.code
              """
        rows = self.runSql(sql)
        return rows
    

    def getDataCollectionInfo(self):
        sql = """
              SELECT c.name,
              c.client_id,
              dc.name,
              dc.data_collection_id,
              dp.code_type,
              dp.http_code,
              dp.redirect_uri,
              dp.payload_text,
              ct.name,
              dpa.name, dpa.expiration_period, dpa.expiration_type, 
              dpa.default_value,
              dpa.do_unset
              FROM ld_client c
              JOIN ld_data_collection dc ON c.client_id = dc.client_id
              LEFT JOIN ld_data_payload dp ON dc.data_collection_id = dp.data_collection_id
              LEFT JOIN ld_data_payload_attribute dpa ON dp.data_payload_id = dpa.data_payload_id
              LEFT JOIN ld_content_type ct ON dp.content_type_id = ct.content_type_id
              """
        rows = self.runSql(sql)
        retval = []
        prev_id = None
        prev_d = None
        d = {}
        for row in rows:
            d['client_name'] = row[0]
            d['client_id']  = row[1]
            d['dc_name'] = row[2]
            d['dc_id'] = row[3]
            print "Found Client %s (%s), DC %s (%s)" % (row[0:4])
            d['code_type'] = row[4]
            d['http_code'] = row[5]
            d['redirect_uri'] = row[6]
            d['payload_text'] = row[7]
            d['ct'] = row[8]
            if d['dc_id'] != prev_id:
                print "Creating payload for new data collection: %s" % d['dc_id']
                d['payload'] = []
            p = {}
            p['name'] = row[9]
            expiry = row[10]
            if expiry:
                expiry = int(expiry)
                expiry_type = row[11]
                if expiry_type == 'minute':
                    expiry *= 60
                elif expiry_type == 'hour':
                    expiry *= 60 * 60
                elif expiry_type == 'day':
                    expiry *= 60 * 60 * 24
                elif expiry_type == 'month':
                    expiry *= 60 * 60 * 24 * 30
            p['expiry'] = expiry
            p['value'] = row[12]
            p['do_unset'] = row[13]
            d['payload'].append(p)
            if not prev_d:
                print "New data collection: %s" % d['dc_id']
                retval.append(deepcopy(d))
            elif prev_d['dc_id'] <> d['dc_id']:
                print "New data collection: %s" % d['dc_id']
                retval.append(deepcopy(d))
            prev_d = deepcopy(d)
        return retval
        

    def getLatestBundle(self):
        rows =  self.runSql("SELECT id, locations, logdefs FROM stat_bundles ORDER BY id DESC LIMIT 1")
        if rows:
            return rows[0]

    def addBundle(self, loc, log):
        cur = self.con.cursor()
        cur.execute("INSERT INTO stat_bundles (locations, logdefs) VALUES (%s,%s)", (loc, log))
        self.con.commit()
        return cur.lastrowid
    
    def getBucketForUser(self, user):
        # Internal things are always enremmeta
        return "s0.enremmeta.com"

    def getColsInfo(self):
        sql = """
             SELECT u.url_prefix, t.name tbl, 
             IF(ISNULL(c.name), CONCAT(mt.prefix, m.name), CONCAT(mt.prefix, c.name)) col
             FROM cols c
             JOIN tbls t ON c.tbl = t.id
             JOIN users u ON t.user = u.id
             LEFT JOIN macro_types mt ON mt.id = c.macro_type 
             LEFT JOIN macros m ON c.macro_type = m.macro_type AND c.macro = m.id
             ORDER BY u.id ASC, t.id ASC, c.id ASC;
             """
        cur = self.con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        retval = {}
        cur_url_prefix = None
        cur_tbl = None
        cur_cols = []
        for row in rows:
            prefix = row[0]
            tbl = row[1]
            col = row[2]
            if prefix == cur_url_prefix:
                # Same prefix as before
                if tbl == cur_tbl:
                    # Same table
                    cur_cols.append(col)
                    continue
                else:
                    # New table
                    if cur_tbl:
                        cur_prefix_dict[cur_tbl] = cur_cols
                    cur_cols = [col]
                    cur_tbl = tbl
                    continue
            else:
                # New prefix
                cur_cols.append(col)
                retval[prefix] = {}
                cur_url_prefix = prefix
                cur_prefix_dict = retval[prefix]
                continue
        if cur_tbl:
            cur_prefix_dict[cur_tbl] = cur_cols
        return retval
            
                
            
    

