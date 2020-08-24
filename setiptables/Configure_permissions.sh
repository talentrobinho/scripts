#!/bin/bash



function usage()
{
	printf "\n"
	printf "################################################################################################################################################\n"
	printf "\n"
	printf "\t%s\n" "Using the parameter list is as follows:"
	printf "\n"
	printf "\t\t%s\n\t\t\t%s\n" "-h [--help]" "See the help"
	printf "\n"
	printf "\t\t%s\n\t\t\t%s\n" "-l [--limit-ip-list-file]" "Specified to limit the SSH login IP list file.(Is to add the IP)"
	printf "\n"
	printf "\t\t%s\n\t\t\t%s\n" "-d [--disabled-cmd]" "Specify the disable command"
	printf "\n"
	printf "\t\t%s\n\t\t\t%s\n" "-s [--modify-ssh-version]" "Modify version of sshd to be specified number."
	printf "\n"
	printf "\t\t%s\n\t\t\t%s\n" "-r [--modify-rsync-allow-host]" "Modify the allow hosts options in the /etc/rsyncd.conf."
	printf "\n"
	printf "\t\t%s\n\t\t\t%s\n" "-p [--modify-root-password]" "Modify the root password for the specified string"
	printf "\n"
	printf "\t\t%s\n\t\t\t%s\n" "For example:" "sh Configure_permissions.sh -s '2,1' -l login.ip -d 'sz scp' -r server.ip -p '123456'"
	printf "\n"
	printf "################################################################################################################################################\n"
	printf "\n"
}


function limit_login()
{
	if [[ $# -ne 1 ]]
	then
		printf "%s\n" "Do not specify the IP list file or limited port"
		exit 1
	fi
	if [[ ! -f $1 ]]
	then
		printf "%s\n" "Specify the IP list file does not exist."
		exit 1
	fi

	/etc/init.d/iptables restart
	local ip_list=$1
	local port=22
	while read ip
	do
		#iptables -A INPUT -i eth0 -p tcp -s $ip --dport $port -j ACCEPT
		iptables -I INPUT 2 -i eth0 -p tcp -s $ip --dport $port -j ACCEPT
	done < ${ip_list}
	DROP_ALL=$(iptables -L | grep -E '^DROP' | awk '{if($4=="anywhere" && $NF=="dpt:ssh")print "ok"}')
	if [[ "${DROP_ALL}" != "ok" ]]
	then
		iptables -A INPUT -i eth0 -p tcp -s 10.134.56.83 --dport 22 -j ACCEPT
		#iptables -A INPUT -i eth0 -p tcp --dport $port -j DROP
	fi

	printf "%s\n" "/etc/sysconfig/iptables.${day}.${timestampt} to create backup file"
	cp /etc/sysconfig/iptables /etc/sysconfig/iptables.${day}.${timestampt}
	### 方法一：
	### iptables-save > /etc/sysconfig/iptables
	### 方法二：
	/etc/init.d/iptables save
}

function modify_rsync_allow()
{

	if [[ $# -ne 1 ]]
	then
		echo "argument error"
		exit 1
	fi

	conf_file="/etc/rsyncd.conf"
	local ip_list_file=$1
	local ip_list=""

	if [[ ! -f ${ip_list_file} ]]
	then
		echo 'The ${ip_list_file} is not exist.'
		exit 1
	fi

	while read ip
	do
		ip_list="$ip_list $ip"	
	done < ${ip_list_file}


	if [[ -f ${conf_file} ]]
	then
		printf "%s\n" "${conf_file}.${day}.${timestampt} to create backup file"
		cp ${conf_file} ${conf_file}.${day}.${timestampt}
		#sed -i 's/^\(hosts allow = .*\)/\1 '"${ip_list}"'/g' ${conf_file}
		sed -i 's/^\(hosts allow =\) .*/\1'"${ip_list}"'/g' ${conf_file}
	fi
}

function disabled_cmd()
{
	if [[ $# -ne 1 ]]
	then
		printf "%s\n" "Please specify the command to disable"
		exit 1
	fi

	for cmd in $@
	do
		which $cmd > /dev/null
		if [[ $? -ne 0 ]]
		then
			printf "%s\n" "The command specified was not found"
			exit 1
		fi
		absolute_cmd=$(which $cmd)
		chmod 700 ${absolute_cmd}

	done
}

function modify_ssh_version()
{
	if [[ $# -eq 1 ]]
	then
		version="$1"
		if [[ -z $version ]]
		then
			version="2,1"
		fi
	fi
	day=$(date +"%Y%m%d")
	conf_file="/etc/ssh/sshd_config"
	if [[ -f ${conf_file} ]]
	then
		printf "%s\n" "${conf_file}.${day}.${timestampt} to create backup file"
		cp ${conf_file} ${conf_file}.$day
		sed -i 's/^\(Protocol\).*/\1 '"$version"'/g' ${conf_file}
	fi
	printf "<INFO> %s\n" "The modified SSH protocol version for ${version}"
	#/etc/init.d/sshd restart
}

function cross_ssh()
{
	cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys.${day}.${timestampt}
	rsync 10.134.56.83::root/search/controller/users/lizhansheng/adht_handong/public.key /tmp/
	cat /tmp/public.key >> ~/.ssh/authorized_keys
}

function modify_root_passwd()
{
	if [[ $# -eq 1 ]]
	then
		password="$1"
		if [[ -z $password ]]
		then
			password="noSafeNoWork@2016"
		fi
	fi
	echo "$password" | passwd --stdin root
	printf "<INFO> %s\n" "Root password has been changed to $password"
}


modify="false"
day=$(date +"%Y%m%d")
timestampt=$(date +"%s")
while getopts "cd:hl:p:r:s:" opt
do
        case $opt in
                c ) cross_ssh
		    ;;
                d ) disabled_cmd "${OPTARG}"
		    ;;
                h ) usage
		    ;;
                l ) limit_login "${OPTARG}"
		    ;;
                p ) modify_root_passwd "${OPTARG}"
		    ;;
                r ) modify_rsync_allow "${OPTARG}"
		    ;;
                s ) modify_ssh_version "${OPTARG}"
		    ;;
                ? ) echo "unkonw argument"
                    exit 1
		    ;;
        esac
done
