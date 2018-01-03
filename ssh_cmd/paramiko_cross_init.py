#!/usr/local/python279/bin/python
#-*-coding:utf8-*-


import paramiko as pm
import ConfigParser
import getopt
import os
import sys
import time
import multiprocessing

def Usage():
    help='''
        The Script Usage:
        -h, --help: Print help messages;
        -f, --config: Specify the configuration file
        -p, --process: Specify the num of process
    '''
    print help


def PrintLog(msg, level='info'):
    ISOTIMEFORMAT="%Y-%m-%d %X"
    stamp="[" + time.strftime(ISOTIMEFORMAT, time.localtime()) + "]"
    info="\033[31m \033[05m%s\033[0m" % (msg,)
    if level == 'info':
        msg="%s \033[37m \033[01m<%s> %s\033[0m" % (stamp, 'INFO', msg)
    elif level == 'warn':
        msg="%s \033[31m \033[01m<%s> %s\033[0m" % (stamp, 'WARNING', msg)
    elif level == 'except':
        msg="%s \033[33m \033[01m<%s> %s\033[0m" % (stamp, 'EXCEPT', msg)
    
    print msg

def decor_str(msg, level='info'):
    ISOTIMEFORMAT="%Y-%m-%d %X"
    stamp="[" + time.strftime(ISOTIMEFORMAT, time.localtime()) + "]"
    info="\033[31m \033[05m%s\033[0m" % (msg,)
    if level == 'info':
        msg="%s\033[37m \033[01m<%s> %s\033[0m" % (stamp, 'INFO', msg)
    elif level == 'warn':
        msg="%s\033[31m \033[01m<%s> %s\033[0m" % (stamp, 'WARNING', msg)
    elif level == 'except':
        msg="%s\033[33m \033[01m<%s> %s\033[0m" % (stamp, 'EXCEPT', msg)
    
    return msg




def ReadCfg(conf):
    if not os.path.exists(conf):
        msg = '''The configuration file is not exist'''
        PrintLog(msg, 'warn')
        sys.exit(1)
    cfg = ConfigParser.ConfigParser()
    try:
        cfg.read(conf)
    except Exception, err:
        PrintLog(str(err), 'except')
        sys.exit(1)
    
    return cfg

def ReadFile(file):
    if not os.path.exists(file):
        msg = '''The %s is not exist.''' % (file,)
        PrintLog(msg)
        sys.exit(1)
    else:
        content_list = []
        try:
            f = open(file, 'r')
            f_content = f.readlines()
            f.close()
            for line in f_content:
                if line.withstart('#'):
                    continue
                else:
                    content_list.append(line.strip(' '))
        except Exception, err:
            PrintLog(str(err), 'except')
            sys.exit(1)
    
    return content_list



def exe_command(ip, username, password, cmd_list, cfg_content):
    conn_output = []
    try:
        pm.util.log_to_file('paramiko.log')
        ss = pm.SSHClient()
        ss.set_missing_host_key_policy(pm.AutoAddPolicy())
        for passwd in password:
            try:
                ss.connect(ip, 22, username, passwd)
                break
            except pm.AuthenticationException, err:
                conn_output.append(decor_str('Password error [%s:%s]'%(ip,passwd), 'warn'))
        root_cmd_list = ['create_user', 'init_system', 'root_ssh', 'install_hadoop']

        for cmd in cmd_list:
            output = []
            if username != 'root' and cmd in root_cmd_list: 
                PrintLog('The command of %s is only use by root [%s].' % (cmd,username), 'warn')
                continue
            if cmd == 'create_user':
                user_info = cfg_content.options(cmd)
                if len(user_info) != 1:
                    PrintLog('The section of create_user is only one option of username_list.', 'warn')
                    #ss.close()
                    #return 1
                    continue
                username_list = cfg_content.get(cmd, 'username_list').strip('"').split(' ')
                for u in username_list:
                    user_home = cfg_content.get(u, 'home_dir')
                    user_passwd = cfg_content.get(u, 'password')
                    create_cmd = "useradd -d %s %s" % (user_home, u)
                    set_passwd = "echo %s | passwd --stdin %s" % (user_passwd, u)
                    stdin, stdout, stderr = ss.exec_command(create_cmd)
                    output.append(stdout.read())
                    stdin, stdout, stderr = ss.exec_command(set_passwd)
                    output.append(stdout.read())
            elif cmd.endswith('_ssh'):
                remote_path = cfg_content.get(cmd, 'rsync_path').strip('"').strip(' ')
                exe_cmd = cfg_content.get(cmd, 'exe_cmd').strip('"').strip(' ')
                #if len(remote_path) != 0 and len(exe_cmd) == 0:
                if len(remote_path) != 0:
                    local_path = "/tmp/keys"+"_"+username
                    rsync_cmd = "%s %s %s" % ('rsync -aP', remote_path, local_path)
                    back_cmd = "%s %s %s" % ('mv', '~/.ssh/authorized_keys', local_path+'.bak')
                    mv_cmd = "%s %s %s" % ('mv', local_path, '~/.ssh/authorized_keys')
                    chown_cmd = "%s %s.%s %s" % ('chown', username, username, '~/.ssh/authorized_keys')
                    mk_cmd = "%s %s" % ('mkdir -p', '~/.ssh')
                    chmod_cmd = "%s %s %s" % ('chmod', '755', '~/.ssh')
                    stdin, stdout, stderr = ss.exec_command(rsync_cmd)
                    output.append(stdout.read())
                    if username == 'root':
                        stdin, stdout, stderr = ss.exec_command(back_cmd)
                        ###print stderr.read()
                        output.append(stdout.read())
                        stdin, stdout, stderr = ss.exec_command(mv_cmd)
                        output.append(stdout.read())
                        print stderr.read()
                    else:
                        stdin, stdout, stderr = ss.exec_command(mk_cmd)
                        output.append(stdout.read())
                        print stderr.read()
                        stdin, stdout, stderr = ss.exec_command(mv_cmd)
                        output.append(stdout.read())
                        print stderr.read()
                        stdin, stdout, stderr = ss.exec_command(chmod_cmd)
                        output.append(stdout.read())
                        print stderr.read()
                    stdin, stdout, stderr = ss.exec_command(chown_cmd)
                    output.append(stdout.read())
                    print stderr.read()


                    if username == 'root':
                        oldprotocol = 'Protocol [12]'
                        newprotocol = 'Protocol 2,1'
                        sed_cmd = "sed -i 's/^%s$/%s/g' /etc/ssh/sshd_config" % (oldprotocol, newprotocol)
                        bak_cmd = "cp /etc/ssh/sshd_config /tmp/"
                        restart_cmd = "/etc/init.d/sshd restart"
                        stdin, stdout, stderr = ss.exec_command(bak_cmd)
                        output.append(stdout.read())
                        print stderr.read()
                        stdin, stdout, stderr = ss.exec_command(sed_cmd)
                        output.append(stdout.read())
                        print stderr.read()
                        stdin, stdout, stderr = ss.exec_command(restart_cmd)
                        output.append(stdout.read())
                        print stderr.read()
                else:
                    PrintLog('The options of exe_cmd must be null', 'warn')
                    #ss.close()
                    #return 1
                    continue

            ### System initialization
            elif cmd == 'init_system':
                remote_path = cfg_content.get(cmd, 'rsync_path').strip('"').strip(' ')
                if username == 'root':
                    ### modify /etc/hosts
                    hostname_cmd = "hostname"
                    stdin, stdout, stderr = ss.exec_command(hostname_cmd)
                    hostname = stdout.read().strip('\r\n')
                    hosts_info = "%s\t%s.sogou-in.domain\t%s" % (ip, hostname, hostname)
                    add_cmd = "echo %s >> /etc/hosts" % (hosts_info,)
                    stdin, stdout, stderr = ss.exec_command(add_cmd)
                    output.append(stdout.read())

                    ### init
                    local_path = "/tmp/init.sh"
                    rsync_cmd = "%s %s %s" % ('rsync -aP', remote_path, local_path)
                    init_cmd = "%s %s" % ('sh', local_path)
                    stdin, stdout, stderr = ss.exec_command(rsync_cmd)
                    output.append(stdout.read())
                    print stderr.read()
                    stdin, stdout, stderr = ss.exec_command(init_cmd)
                    output.append(stdout.read())
                    print stderr.read()

            elif cmd == 'install_hadoop':
                remote_path = cfg_content.get(cmd, 'rsync_path').strip('"').strip(' ')
                local_path = "/opt/"
                rsync_cmd = "%s %s %s" % ('rsync -aP', remote_path, local_path)
                stdin, stdout, stderr = ss.exec_command(rsync_cmd)
                output.append(stdout.read())
                print stderr.read()

            else:
                remote_path = cfg_content.get(cmd, 'rsync_path').strip('"').strip(' ')
                exe_cmd = cfg_content.get(cmd, 'exe_cmd').strip('"').strip(' ')
                if len(remote_path) == 0 and len(exe_cmd) == 0:
                    PrintLog('Two options of %s are not empty'%(cmd,), 'warn')
                    #ss.close()
                    #return 1
                    continue
                if len(remote_path) != 0:
                    local_path = "/tmp/"
                    rsync_cmd = "%s %s %s" % ('rsync -aP', remote_path, local_path)
                    stdin, stdout, stderr = ss.exec_command(rsync_cmd)
                    output.append(stdout.read())
                    print stderr.read()
                else:
                    rsync_cmd=""
                if len(exe_cmd) != 0:
                    ### 禁止删除操作
                    decom_cmd = exe_cmd.replace(';', ' ').split(' ')
                    if 'rm' in decom_cmd:
                        PrintLog('In the command executed contains the rm [%s].' % (exe_cmd,), 'warn')
                        #ss.close()
                        #return 1
                        continue
                    exe_script = "%s" %(exe_cmd,)
                    stdin, stdout, stderr = ss.exec_command(exe_script)
                    output.append(stdout.read())
                    print stderr.read()
                else:
                    exe_script = ""

            output.append('%s'%(decor_str('%s %s done' % (ip, cmd),)))
            print ''.join(conn_output)
            print ''.join(output)


        ### for 循环之外
        ss.close()
        
        
    except Exception, err:
        PrintLog(str(err)+' ['+ip+']', 'except')


def execute(cfg, process):
    cfg_content = ReadCfg(cfg)
    try:
        user_opt = cfg_content.options('main')
        user_list = cfg_content.get('main', user_opt[0]).strip('"').split(' ')
        for user in user_list:
            user_info = cfg_content.options(user)
            hosts = cfg_content.get(user, user_info[0]).strip(' ').strip('"')
            username = cfg_content.get(user, user_info[1]).strip(' ').strip('"')
            home = cfg_content.get(user, user_info[2]).strip(' ').strip('"')
            password = cfg_content.get(user, user_info[3]).strip(' ').strip('"').split(',')
            ### add command "echo $?" at command'end
            ###command = cfg_content.get(user, user_info[4]).strip(' ').strip('"')+" /tmp/authorized_keys_tmp;echo $?"
            command_list = cfg_content.get(user, user_info[4]).strip(' ').strip('"').split(' ')

            ### read file of ip list
            ip_file = open(hosts, 'r')
            ip_list = ip_file.readlines()
            ip_file.close()

            pool = multiprocessing.Pool(processes=process)
            for ip in ip_list:
                ### 去除#开头的注释ip和空行
                if ip.startswith('#') or ip == '':
                    continue
                ip = ip.strip('\r\n')
                ### 多进程进行ssh信任关系部署
                pool.apply_async(exe_command, (ip, username, password, command_list, cfg_content))
                PrintLog('%s done.' % (ip,))
            pool.close()
            pool.join()
            PrintLog('All process done.')
            #sys.exit(1)


    except Exception, err:
        PrintLog(str(err), 'except')
        sys.exit(1)




def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'hf:p:', ['help', 'config=', 'process='])
    except getopt.GetoptError, opterr:
        PrintLog(str(opterr), 'except')
        Usage()
        sys.exit(1)
    try:
        cfg_value = ""
        process_value = ""
        for opt, value in opts:
            if opt in ('-h', '--help'):
                Usage()
                sys.exit(1)
            elif opt in ('-f', '--config'):
                cfg_value = value
                #execute(value)
            elif opt in ('-p', '--process'):
                #execute(value)
                process_value = value
            else:
                msg = '''The %s option is not unknown.''' % (opt,)
                PrintLog(msg, 'warn')
                sys.exit(1)

        if len(cfg_value) > 0:
            if len(process_value) == 0 or int(process_value) > multiprocessing.cpu_count():
                msg = "The -p option is not within the scope[1-%d], will use the default value is %d" % (multiprocessing.cpu_count(),1) 
                PrintLog(msg, 'warn')
                #p = multiprocessing.cpu_count()
                p = 1
            #elif int(process_value) != 0 and int(process_value) <= multiprocessing.cpu_count():
            elif int(process_value) > 0:
                p = int(process_value)
            execute(cfg_value, p)
        else:
            msg = "The -f option is not specify"
            PrintLog(msg, 'warn')
            sys.exit(1)
    except Exception, err:
        PrintLog(str(err), 'except')
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        Usage()
        sys.exit(1)
    main(sys.argv)
