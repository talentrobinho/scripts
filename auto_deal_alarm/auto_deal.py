#-*- coding: UTF-8 -*-

import urllib
import urllib2
import cookielib
import Cookie
import chardet
from bs4 import BeautifulSoup
import re
import sys


def deal_alar(sms_head, deal_info = "已处理"):

    '''
    	变量定义字段
    '''
    LoginURL = 'http://sss.ddd.xxx.com/login.php'
    AlarURL = 'http://sss.ddd.xxx.com/process.php'
    SMSURL = 'http://sss.ddd.xxx.com/index.php?ness=my'
    UserInfo = {
    		'user_name': 'tom',
    	     	'user_pass': '123456',
                }
    
    '''
    	将post的数据转为url编码
    '''
    postUserData = urllib.urlencode(UserInfo);
    
    
    cj = cookielib.CookieJar();
    op = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj));
    urllib2.install_opener(op);
    
    '''
    	进行登录请求获取cookie
    '''
    req = urllib2.Request(LoginURL, postUserData);
    
    '''
    	设置请求头信息
    '''
    req.add_header('Content-Type', 'application/x-www-form-urlencoded');
    req.add_header('Cache-Control', 'no-cache');
    req.add_header('Accept', '*/*');
    req.add_header('Connection', 'Keep-Alive');
    
    
    
    '''
    	存储cookie
    '''
    resp = urllib2.urlopen(req);
    
    
    '''
    	获取短信页面html
    '''
    resp3 = urllib2.urlopen(SMSURL);
    soup = BeautifulSoup(resp3.read(), "html.parser")
    
    
    
    '''
    	筛选业务类型正则表达式
    '''
    pat = re.compile(r'business=(.*)&amp;alert_type')
    data_list = []
    sms_id_list = []
    
    """
    	分析短信平台html中table元素
    	找出短息id、处理状态、业务类型 
    """
    for idx, tr in enumerate(soup.find_all('tr')):
        if idx < 3:
    	    continue
    
        tds = tr.find_all('td')
        if len(tds) >= 9:
            status_content = tds[2].contents[0].encode('utf-8')
    	    '''
    	    	过滤出未处理的报警
    	    '''
            if status_content == '待处理'.decode('GB2312').encode('utf-8'):
    	        '''
    	        	正则匹配出业务类型
    	        '''
    	        #for link in tds[5].contents[0].find_all('a'):
    	        #    type_content = pat.findall(str(link), re.S)
    
    
    	        '''
    	        	正则匹配骋报警头
    	        '''
    	        for link in tds[5].contents[0].find_all('a'):
    	            if sms_head in link.contents:
    		            '''
    			        将数据存储在列表里，稍后使用
    		            '''
        	            sms_info = {
        	                'smsid': tds[0].contents[0],
        	                'status': tds[2].contents[0],
        	                'alartype': ''
        	    	    }
        	            data_list.append(sms_info)
    		            sms_id_list.append(tds[0].contents[0])
    
    if len(sms_id_list) == 0:
	    print "Not found sms head"
	    sys.exit(1)

    smslist = ','.join(sms_id_list)
    AlarInfo = {
    		'is_self_post': '',
    		'sms_status': 'finish_process',
    		'hero': '1',
    		'sms_ids': smslist,
    		'sms_comment_name': '@tom',
    		'sms_comment': '%s'%(deal_info,),
    		'sms_business': '',
    		'url_query_string': 'business=my',
    		'url_script_name': '/index.php'
    	   }
    
    
    postAlarData = urllib.urlencode(AlarInfo);
    
    '''
    	签报警
    '''
    resp2 = urllib2.urlopen(AlarURL, postAlarData);

if __name__ == '__main__':
    if len(sys.argv) == 3:
        sh = sys.argv[1]
        di = sys.argv[2]
        deal_alar(sh, di)
    elif len(sys.argv) == 2:
        sh = sys.argv[1]
        deal_alar(sh)
    else:
        print 'Please input sms_head'
        sys.exit(1)
