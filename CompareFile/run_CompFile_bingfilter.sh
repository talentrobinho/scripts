#!/bin/bash

function comp_filterlog()
{
    local day="$(date -d '1 days ago' +"%Y%m%d")"
    local month="$(date -d $day +"%Y%m")"
    local hadoop_path="/data/bidding/bing_filter_log/$month/$day"
    local file="$hadoop_path/bing_filter_log"    
    local hadoop1_name="bmw"
    local hadoop2_name="maserati"
    local smshead="[Common/Data/BingFilterLog]"
    
    while true
    do
        adop-hadoop-ls -f ${hadoop1_name} "$file.done" > /dev/null 2> comp.log
        flag1=$?
        adop-hadoop-ls -f ${hadoop2_name} "$file.done" > /dev/null 2> comp.log
        flag2=$?
        if [[ $flag1 -eq 0 && $flag2 -eq 0 ]]
        then
            ./CompFile.py --smshead "${smshead}" --max-threshold 200000 --min-threshold -200000 --file1 "${file}" --file1-type "hadoop" --file1-hadoop-name "${hadoop1_name}" --file2 "${file}" --file2-type "hadoop" --file2-hadoop-name "${hadoop2_name}"
            break
        else
            sleep 300
        fi
    done
}


comp_filterlog
