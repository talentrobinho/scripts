#!/bin/bash

####################
### var zone
####################
disk_threshold=100
machine_name=$(hostname)

####################
### func zone
####################
alert()
{
    msg="$machine_name:
    $1"
    curl "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=****" \
	-H "Content-Type: application/json" \
	-d \
    	"{ 
        	\"msgtype\": \"text\",
        	\"text\": {
            		\"content\": \"$msg\",
	    		\"mentioned_list\":[\"@all\"]
        	}
   	}"

}

monitor_disk()
{
    cmd=$(which df)
    $cmd -h | awk -v threshold=$disk_threshold '$0~/^\/dev\// {
			split($5,a,"%")
			if(a[1]>threshold)
			{
			    printf("%s\t%s\t%s\t%s\n",$1,$4,$5,$6)
			}
		}'
}


####################
### main zone
####################
alert_disk_content="$(monitor_disk)"

if [[ "$alert_disk_content" =~ "dev" ]]
then
    alert "$alert_disk_content"
fi

