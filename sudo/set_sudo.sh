#!/bin/bash

sudo_d='/etc/sudoers.d'
sudo_f='/etc/sudoers'
key='#includedir /etc/sudoers.d'
def_sudo_d_per="0750"
def_sudo_f_per="0440"
key_count=0

if [ -f $sudo_f ]
then
    key_count=$(grep -c "$key" $sudo_f)
else
    echo "$sudo_f is not exist."
    exit 1
fi

if [ ! -d $sudo_d ]
then
    mkdir -p $sudo_d
fi

if [ $key_count -eq 0 ]
then
    sed -i '$a'"$key" $sudo_f
fi


wget -q http://scripts.adto.ad.com/Sudo/default -O $sudo_d/default

sudo_d_per=$(stat $sudo_d | awk '$2~/^\([0-9].*\)$/{split(substr($2,2,length($2)-1), a, "/"); print a[1]}')

if [ "$sudo_d_per" != "$def_sudo_d_per" ]
then
    chmod $def_sudo_d_per $sudo_d
fi
chmod $def_sudo_f_per ${sudo_d}/*
