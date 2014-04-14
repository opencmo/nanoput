#!/bin/bash
 
dir=`basename $0`
rm -rf /opt/enr/log/processing/$dir
mkdir -p /opt/enr/log/processing/$dir
cd /opt/enr/log/processing/$dir
echo In `pwd`
if [ "$1" != "" ]; then
  goback=$1
fi


date=`date -u -d "$goback hour ago"  +"year=%Y/month=%m/day=%d/hour=%H"`
human_date=`date -u -d "$goback hour ago"  +"%Y-%m-%d, hour %H"`
rm -rf imp1 imp2
mkdir imp1
mkdir win
mkdir imp2
cur=`pwd`
echo In `pwd`

cd imp1
echo In `pwd`
url=s3://stats.opendsp.com/$date/type=impression/
echo Fetching `s3cmd ls $url | wc -l` files from $url
s3cmd --access_key=AKIAJIN5ZQGGSAVWTWFQ --secret_key="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" sync $url . > /dev/null 2>&1
gunzip *
cd $cur

cd win
echo In `pwd`
url=s3://stats.opendsp.com/$date/type=win/
echo Fetching `s3cmd ls $url | wc -l` files from $url
s3cmd --access_key=AKIAJIN5ZQGGSAVWTWFQ --secret_key="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" sync $url . > /dev/null 2>&1
gunzip *
cd $cur

echo In `pwd`
cd imp2
echo In `pwd`
url=s3://sva.s2.opendsp.com/user=man/table=impression/$date/
echo Fetching `s3cmd ls $url | wc -l` files from $url
s3cmd  --access_key=AKIAJIN5ZQGGSAVWTWFQ --secret_key="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" sync $url .  > /dev/null 2>&1
gunzip *
cd $cur
echo In `pwd`

imp1=`cat imp1/* | grep -v scheduleLogRolloverEnforcer | wc -l`
imp1=`echo $imp1 | sed -e 's/ //g'`

win=`cat win/* | grep -v scheduleLogRolloverEnforcer | wc -l`
win=`echo $win | sed -e 's/ //g'`


imp2=`cat imp2/* | wc -l`
imp2=`echo $imp2 | sed -e 's/ //g'`

discrep=`echo "($imp1-$imp2.)/$imp2*100" | bc -l`
discrep=`printf "%.0f" $discrep`
echo For $human_date, imp1=$imp1, imp2=$imp2, win=$win, discrepancy $discrep'%' > /tmp/$dir
threshold=10
neg_threshold=`echo "-1*$threshold" | bc`
if [ $discrep -gt $threshold ] || [ $discrep -lt $neg_threshold ]; then
   echo "Discrepancy $discrep is bigger than preset threshold $threshold (or $neg_threshold)" >> /tmp/$dir
   echo "Breakdown by exchange" >> /tmp/$dir
   echo "Impression 1 (count/exchange/suspicious)"  >> /tmp/$dir
   cat imp1/* | grep -v scheduleLogRolloverEnforcer | cut -f21,49 | sort | uniq -c >> /tmp/$dir
   echo "Win (count/exchange/suspicious)"  >> /tmp/$dir
   cat win/* | grep -v scheduleLogRolloverEnforcer | cut -f21,47 | sort | uniq -c >> /tmp/$dir
   echo "Impression 2"  >> /tmp/$dir
   cat imp2/* | cut -f29 | sort | uniq -c >> /tmp/$dir

#   echo "Impression 1 (count/exchange/TS)"  >> /tmp/$dir
#   cat imp1/* | grep -v scheduleLogRolloverEnforcer | cut -f21,6 | sort | uniq -c >> /tmp/$dir
#   echo "Impression 2"  >> /tmp/$dir
#   cat imp2/* | cut -f23,29 | sort | uniq -c >> /tmp/$dir

   # cat /tmp/$dir | mailto adops@opendsp.com -s "Discrep between imp and imp2"
fi
cat /tmp/$dir