#!/usr/bin/python
#-*- coding: UTF-8 -*-



import sys
import os
import subprocess
import logging
from optparse import OptionParser

hadoop_benz     = "/opt/hadoop-client/hadoop_benz/bin/hadoop"
hadoop_bmw      = "/opt/hadoop-client/hadoop25-bmw/hadoop/bin/hadoop"
hadoop_maserati = "/opt/hadoop-client/hadoop_maserati/bin/hadoop"
sendsms         = "/opt/monitor/sendsms.sh"


logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                #filename='myapp.log',
                #filemode='w'
                )

def fetchsize(filename, stype, hadoop_name=''):
    if stype == 'local':
        filesize = os.path.getsize(filename)

    elif stype == 'hadoop':
        if hadoop_name == 'benz':
            hadoop_client = hadoop_benz
        elif hadoop_name == 'bmw':
            hadoop_client = hadoop_bmw
        elif hadoop_name == 'maserati':
            hadoop_client = hadoop_maserati
        fileinfo = subprocess.Popen('%s fs -ls %s'%(hadoop_client, filename), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in fileinfo.stdout.readlines():
            tmp_str = ','.join(line.split())
            info_list = tmp_str.split(',')
            
            if len(info_list) < 8:
                continue
            filesize = info_list[4]

    return filesize


def main():
    usage = """
    This script is used to compare the file size
            """
    parser = OptionParser(usage=usage)
    parser.add_option("", "--date",         type="string", dest="day",
                                                help="Compare the date on which the")
    parser.add_option("", "--file1",        type="string", dest="file1", 
                                                help="The first filename")
    parser.add_option("", "--file1-hadoop-name",  type="string", dest="file1_hadoop_name", 
                                                help="Hadoop cluster name")
    parser.add_option("", "--file1-type",         type="string", dest="file1_store_type", 
                                                help="Files are stored in the machine or hadoop. Only two values local or hadoop")
    parser.add_option("", "--file2",        type="string", dest="file2", 
                                                help="The second filename")
    parser.add_option("", "--file2-hadoop-name",  type="string", dest="file2_hadoop_name", 
                                                help="Hadoop cluster name")
    parser.add_option("", "--file2-type",         type="string", dest="file2_store_type", 
                                                help="Files are stored in the machine or hadoop. Only two values local or hadoop")
    parser.add_option("", "--smshead",         type="string", dest="smshead", 
                                                help="Specify the alarm sms head")
    parser.add_option("", "--max-threshold",         type="string", dest="max_threshold", 
                                                help="Specify the alarm threshold")
    parser.add_option("", "--min-threshold",         type="string", dest="min_threshold", 
                                                help="Specify the alarm threshold")
    (options, args) = parser.parse_args()


    if options.file1_store_type == "hadoop" and options.file1_hadoop_name is None:
        logging.info("When '--file1-type' is hadoop, '--file2-hadoop-name' parameters must be used")
    elif options.file2_store_type == "hadoop" and options.file2_hadoop_name is None:
        logging.info("When '--file2-type' is hadoop, '--file2-hadoop-name' parameters must be used")
    else:
        file1size = fetchsize(options.file1, options.file1_store_type, options.file1_hadoop_name)
        file2size = fetchsize(options.file2, options.file2_store_type, options.file2_hadoop_name)
        diffsize = int(file1size) - int(file2size)
        
        if diffsize > int(options.max_threshold):
            content = "%s of %s is less than %s[%s]"%(options.file1.split('/')[-1], options.file1_hadoop_name, options.file2_hadoop_name, diffsize)
            logging.warning(content)
            #sendsmsinfo = subprocess.Popen('sh %s "%s" "%s"'%(sendsms, options.smshead, content), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            subprocess.Popen('sh %s "%s %s"'%(sendsms, options.smshead, content), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            flag = 1
        elif diffsize < int(options.min_threshold):
            content = "%s of %s is less than %s[%s]"%(options.file2.split('/')[-1], options.file2_hadoop_name, options.file1_hadoop_name, diffsize)
            logging.warning(content)
            #sendsmsinfo = subprocess.Popen('sh %s "%s" "%s"'%(sendsms, options.smshead, content), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            subprocess.Popen('sh %s "%s %s"'%(sendsms, options.smshead, content), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            flag = 2
        else:
            logging.info("%s in %s and %s in %s size differ %s"%(options.file1.split('/')[-1], options.file1_hadoop_name, options.file2.split('/')[-1], options.file2_hadoop_name, diffsize))
            flag = 0
    return flag

if __name__ == "__main__":
    check_result=main()
    sys.exit(check_result);
