#!/bin/bash
set -x
dt=$(perl -e 'use POSIX;print strftime "%Y%m%d",localtime time-86400;')
rm -rf /opt/enr/log/grisha/lotame/2015*
dt=$(perl -e 'use POSIX;print strftime "%Y%m%d",localtime time-86400;')
dt=${dt}11
s3cmd --access_key=AKIAJIN5ZQGGSAVWTWFQ --secret_key="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" sync s3://amphora.opendsp.com/home/lotame.opendsp.com/$dt /opt/enr/log/grisha/lotame
gunzip /opt/enr/log/grisha/lotame/$dt/audiencemembership.tsv.gz
/opt/enr/py/lotame_dynamo.py /opt/enr/log/lotame/$dt/audiencemembership.tsv