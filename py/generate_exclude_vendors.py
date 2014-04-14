import MySQLdb
import hashlib

from datetime import datetime
from sys import exit
from plumbum.cmd import mv
from plumbum import local

from common import CREDS


def log(message):
    print '{}: {}'.format(str(datetime.now()), message)


def get_connect():
    host_ = CREDS['mysql_host']
    user_ = CREDS['mysql_user']
    pass_ = CREDS['mysql_passwd']
    conn = MySQLdb.connect(host=host_, user=user_, passwd=pass_)
    return conn


def db_request(conn, _query):
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(_query)
    query_result = cursor.fetchall()
    log('{} rows were exported from DB'.format(len(query_result)))
    result = {}
    for row in query_result:
        if row['pixel_id'] in result:
            result[row['pixel_id']] = '{},{}'.format(result[row['pixel_id']],
                                                     row['data_sync_partner_id'])
        else:
            result[row['pixel_id']] = '{}'.format(row['data_sync_partner_id'])
    return result


def close_connection(conn):
    conn.close()


def get_md5(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


def swap_files(first, second):
    try:
        mv(first, second)
    except Exception:
        log('Can not change regular file')
        exit(3)
    else:
        log('Regular file was changed')


def nginx_reload():
    nginx = local['/etc/init.d/nginx']
    try:
        nginx('reload')
    except Exception as e:
        log('Can not reload nginx: {}'.format(e))
        exit(4)
    else:
        log('Nginx was reloaded')


try:
    connection = get_connect()

    query = ('''SELECT pixel_id, data_sync_partner_id
                FROM opendsp.ld_pixel_exclude_data_sync_provider
                ORDER BY pixel_id;''')

    exclude_vendors = db_request(connection, query)
    close_connection(connection)
except Exception as e:
    log('Something wrong with DB part: {}'.format(e))
    exit(1)
else:
    log('{} pixels were found in exported data'.format(len(exclude_vendors)))


path_regular_file = '/opt/enr/lua/exclude_vendors.lua'
path_temp_file = '/tmp/exclude_vendors.lua'

try:
    regular_file_md5 = get_md5(path_regular_file)
except Exception:
    regular_file_md5 = ''
    log('Regular file not found. MD5 sum is ""')
else:
    log('MD5 sum of regular file is "{}"'.format(regular_file_md5))

try:
    f = open(path_temp_file, 'w')
    f.write('local exclude_vendors = {}\n\n')

    for pxid, excl_vendors in exclude_vendors.iteritems():
        f.write('exclude_vendors["{}"] = "{}"\n'.format(pxid, excl_vendors))

    f.write('\nreturn exclude_vendors')
    f.close()
except Exception as e:
    log('Something wrong with part for generate file: {}'.format(e))
    exit(2)

temp_file_md5 = get_md5(path_temp_file)
log('MD5 sum of temp file is "{}"'.format(temp_file_md5))


if temp_file_md5 != regular_file_md5:
    swap_files(path_temp_file, path_regular_file)
    nginx_reload()
else:
    log('Both files are the same.')
