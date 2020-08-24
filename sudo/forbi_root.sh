#!/bin/bash


forbi_str="auth		required	pam_wheel.so use_uid"
forbi_conf="/etc/pam.d/su"
add_conf="/etc/login.defs"
add_str="SU_WHEEL_ONLY yes"


find_str="$(grep 'pam_wheel.so use_uid' $forbi_conf | sort -u)"

if [ "#$forbi_str" == "$find_str" ]
then
	sed -i '/'"$find_str"'/a'"$forbi_str"'' $forbi_conf
	echo "$add_str" >> $add_conf
	exit
fi

echo -e "$forbi_str"
echo -e "$find_str"
