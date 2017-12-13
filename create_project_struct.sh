#!/bin/bash


cat<<eee
### Please enter a project name.
eee
read -p "### The project name: " pname

echo -e "### You are sure to create the [ $pname ] project?"
read -p "### Your choice [y/n]: " answer

if [[ "$answer" != "y" ]]
then
    exit    
fi

DIRECTLIST=(
"$pname/$pname"
"$pname/docs"
"$pname/$pname/test"
)

FILELIST=(
"$pname/LICENSE"
"$pname/README.md"
"$pname/TODO.md"
"$pname/docs/conf.py"
"$pname/requirements.txt"
"$pname/setup.py"
"$pname/$pname/__init__.py"
"$pname/$pname/$pname.py"
)

for crd in `echo ${DIRECTLIST[@]}`
do
        mkdir -p $crd
        if [[ $? -ne 0 ]]
        then
            exit
        fi
done

for crf in `echo ${FILELIST[@]}`
do
        touch $crf
        if [[ $? -ne 0 ]]
        then
            exit
        fi
done

echo "### Create $pname project success!!!"
