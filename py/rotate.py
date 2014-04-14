#!/opt/enr/virtupy/bin/python
# $Id$

import sys
import os
import time
import datetime
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from common import *

MAX_LOG_SIZE = 1 * 1000 * 1000 * 1000 

def get_dc_logs():
    """
    Get list of currentl managed data collection logs. 
    TODO: Get it from DB
    For now we'll just use rules that we know currently to be the case.

    """
    files = os.listdir(LOG_DIR)
    for f in files:
        if not f.endswith('.enr.log'):
            continue

        ff = os.path.join(LOG_DIR, f)
        elts = f.split('.')
        if len(elts) != 4:
            continue
        yield f

def rotate1(dt, f):
    """
    If now is the first minute of the hour or file size exceeds 

    Else return None

    """

>>>>>>> f01f9fa1f38d4b7de4fe6a8d36cd6671944f03e8
def main():
    """
    This script is intended to be run from cron every minute. This main is "threaded code" so
    just read the body of the procedure for steps.

    """
    # 1. Figure out the time
    ts = time.time()
    dt = datetime.datetime.fromtimestamp(ts)
    suffix = time.strftime("%Y%m%d.%H%M%S")
    log("Unix time: %s; suffix: %s" % (ts, suffix))

    # 2. Get list of currently available files
    for f in get_dc_logs():
        do_rotate = None
        if dt.minute == 0:
            do_rotate = 'On the hour'
        elif 
        print f
        
        
if __name__ == "__main__":
    main()
