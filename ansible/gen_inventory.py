#!/usr/local/python279/bin/python

import sys
import logging
import MySQLdb
from optparse import OptionParser
import json

reload(sys)
sys.setdefaultencoding('utf-8')


mysql_host = '127.0.0.1'
mysql_user = 'hello'
mysql_passwd = 'hello_world'
mysql_db = 'hello'
mysql_port = '3306'

logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='/tmp/test.log',  
                    filemode='w') 

def readDB(sql,db_data=()):
    try:
        conn = MySQLdb.connect(db=mysql_db,user=mysql_user,passwd=mysql_passwd,host=mysql_host,port=int(mysql_port),charset="utf8")
        cursor = conn.cursor()
    except Exception,e:
        logging.error("mysql connect fail: %s"%(e,))
        return False
    try:
        cursor.execute(sql,db_data)
        #data = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        query_result = cursor.fetchall()
    except Exception,e:
        logging.error("SQL exec fail: %s"%(e,))
        return False
    finally:
        cursor.close()
        conn.close()
    return query_result


def process_group_data(data):
    tmplist = {}
    result = {}
    varlist = {}
    varlist['hostvars'] = {}
    if data:
        for row in data:
            ip_list, passwd_list, server = row
            if len(tmplist) == 0 or server.strip() not in tmplist.keys():
                tmplist[server]=[[],[]]
            tmplist[server][0].append("%s"%ip_list)
            tmplist[server][1].append("%s"%passwd_list)
            
                
        for k in tmplist.keys():
            hostlist = tmplist[k][0]
            passwdlist = tmplist[k][1]
            result[k.strip('/').replace('/', '_')] = {}
            #result[server.strip('/').replace('/', '_')]['hosts'] = hostlist
            result[k.strip('/').replace('/', '_')] = hostlist
            for i in range(len(hostlist)):
                varlist['hostvars'][hostlist[i]] = {}
                varlist['hostvars'][hostlist[i]]['ansible_ssh_host'] = hostlist[i]
                varlist['hostvars'][hostlist[i]]['ansible_connection'] = 'ssh'
                varlist['hostvars'][hostlist[i]]['ansible_ssh_port'] = 22
                varlist['hostvars'][hostlist[i]]['ansible_ssh_user'] = 'root'
                varlist['hostvars'][hostlist[i]]['ansible_ssh_pass'] = passwdlist[i]
            result['_meta'] = varlist
    return result

def process_host_data(data):
    info_dict = {}
    hostlist = []
    passwd = []
    if data:
        for row in data:
            #print row
            ip_list, passwd_list, service = row
            #hostlist = ip_list.split(',')
            hostlist.append(ip_list)
            #passwd = passwd_list.split(',')
            passwd.append(passwd_list)
            info_dict['ansible_ssh_host'] = hostlist[0]
            info_dict['ansible_connection'] = 'ssh'
            info_dict['ansible_ssh_port'] = 22
            info_dict['ansible_ssh_user'] = 'root'
            info_dict['ansible_ssh_pass'] = passwd[0]
    return info_dict



service = "/yyy/sss/xxx"


def main():
    usage = """
    This script is used to gen inventor file to ansible
            """
    parser = OptionParser(usage=usage)
    parser.add_option("", "--host", type="string", dest="host",
                                                help="")
    parser.add_option("", "--list", action="store_true", dest="host_list",
                                                help="return all host group")
    (options, args) = parser.parse_args()


    if options.host is None and options.host_list is None:
        logging.warning("Please specail param --list or --host")
        sys.exit(1)
    elif options.host and options.host_list:
        logging.warning("param --list is use with --host")
        sys.exit(1)
    elif options.host:
        HOST_SQL = "select IP, password, service from machine_new where IP = '%s'"%(options.host,)
        result = process_host_data(readDB(HOST_SQL))
    elif options.host_list:
        #GROUP_SQL = "select group_concat(IP),group_concat(password),service from machine_new where service like '%s%%%%' group by service"%(service,)
        GROUP_SQL = "select IP,password,service from machine_new where service like '%s%%%%'"%(service,)
        result = process_group_data(readDB(GROUP_SQL))
    print json.dumps(result)


if __name__ == '__main__':
    main()
