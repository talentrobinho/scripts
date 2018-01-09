#!/bin/bash

num=3
if [[ $# -eq 1 ]]
then
    num=$1
fi
function comp_filterlog()
{
    local before=$1
    local hour=$(date -d "$before hours ago" +'%H')
    local day=$(date -d "$before hours ago" +'%Y%m%d')
    local month=$(date -d $day +'%Y%m')
    local hadoop_path="/data/bidding/biddingserver/filter_log/$month/$day"
    local file="$hadoop_path/filter_log_$day.$hour"    
    local hadoop1_name="bmw"
    local hadoop2_name="maserati"
    local smshead="[Common/Data/FilterLog]"
    local YEAR=$(date -d "$day" +'%Y')
    local MONTH=$(date -d $day +'%m')
    local DAY=$(date -d $day +'%d')
    local hadoop_maserati="/opt/hadoop-client/hadoop_maserati/bin/hadoop"
    local hadoop_bmw='/opt/hadoop-client/hadoop25-bmw/hadoop/bin/hadoop'
    
    while true
    do
        adop-hadoop-ls -f ${hadoop1_name} "$hadoop_path/done.$hour" > /dev/null 2> comp_filter.log
        flag1=$?
        adop-hadoop-ls -f ${hadoop2_name} "$hadoop_path/done.$hour" > /dev/null 2> comp_filter.log
        flag2=$?
        if [[ $flag1 -eq 0 && $flag2 -eq 0 ]]
        then
            ./CompFile.py --smshead "${smshead}" --max-threshold 200000 --min-threshold -200000 --file1 "${file}" --file1-type "hadoop" --file1-hadoop-name "${hadoop1_name}" --file2 "${file}" --file2-type "hadoop" --file2-hadoop-name "${hadoop2_name}"
            if [[ $? -eq 1 ]]
            then
                sh /search/logcenter_fix/biddingserver/fix_lead_ie_log.sh $day $hour
                ssh root@10.134.24.138 "cd /search/task/FilterLogFlow/filter_log_bmw/script; sh run_getfilter_new.sh $YEAR $MONTH $DAY $hour"
                $hadoop_maserati fs -rmr /data/bidding/biddingserver/filter_log/$month/$day/{done.$hour,filter_log_$day.$hour}
                $hadoop_maserati fs -rmr /data/bidding/biddingserver/lead_filter_log_cheat/$month/$day/{done.$hour,lead_filter_log_cheat.$day.$hour}
            elif [[ $? -eq 2 ]]
            then
                sh /search/logcenter_fix/biddingserver/fix_lead_ie_log.sh $day $hour
                ssh root@10.134.74.88 "cd /search/task/FilterLogFlow/filter_log/script; sh run_getfilter_new.sh $YEAR $MONTH $DAY $hour"
                $hadoop_bmw fs -rm -r /data/bidding/biddingserver/filter_log/$month/$day/{done.$hour,filter_log_$day.$hour}
                $hadoop_bmw fs -rm -r /data/bidding/biddingserver/lead_filter_log_cheat/$month/$day/{done.$hour,lead_filter_log_cheat.$day.$hour}
            fi
            break
        else
            sleep 300
        fi
    done
}


comp_filterlog $num
