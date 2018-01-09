#!/bin/bash

num=1
if [[ $# -eq 1 ]]
then
    num=$1
fi
function comp_filterlog()
{
    local before=$1
    local day=$(date -d "$before days ago" +'%Y%m%d')
    local month=$(date -d $day +'%Y%m')
    local hadoop_path="/data/bidding/ada_result/$day"
    local file="$hadoop_path/ws_cheat_pvid"
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
        adop-hadoop-ls -f ${hadoop1_name} "$file.done" > /dev/null 2> comp_filter.log
        flag1=$?
        adop-hadoop-ls -f ${hadoop2_name} "$file.done" > /dev/null 2> comp_filter.log
        flag2=$?
        if [[ $flag1 -eq 0 && $flag2 -eq 0 ]]
        then
            ./CompFile.py --smshead "${smshead}" --max-threshold 100 --min-threshold -100 --file1 "${file}" --file1-type "hadoop" --file1-hadoop-name "${hadoop1_name}" --file2 "${file}" --file2-type "hadoop" --file2-hadoop-name "${hadoop2_name}"
            break
        else
            sleep 300
        fi
    done
}


comp_filterlog $num
