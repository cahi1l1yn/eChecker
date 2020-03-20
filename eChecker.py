#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
----------------------------------------------------
eChecker
Make auto checkin and checkout for eteams
Author: cahi1l1yn
Version:1.0
--------------------------------------------------
'''

import getopt
import sys
import urllib2
import time
import logging
import json
import re
import cookielib

help='''
Usage: eChecker.py -i checkin_time(%hh:%mm) -o checkout_time(%hh:%mm) -u username -p password

-h Print this help
-i Set checkin time(%hh:%mm)
-o Set checkout time(%hh:%mm)
-u Your username
-p Your password
'''

banner='''
----------------------------------------------------
eChecker
Make auto checkin and checkout for eteams
Author: cahi1l1yn
Version:0.9
----------------------------------------------------
'''

kurl = 'https://www.eteams.cn/portal/tasks.json?name=%E4%BB%BB%E5%8A%A1&isShow=1&id=2&type=mine&userId=4975080324437330342&_=1584491917775'
curl = 'https://www.eteams.cn/attendapp/timecard/check.json'
lurl = 'https://passport.eteams.cn/login'
agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36'
usage = "Usage: eChecker.py -i [checkin_time](%hh:%mm) -o [checkout_time](%hh:%mm) -u username -p password\n"


def get_time():
    global h,m,d
    h = time.strftime('%H',time.localtime())
    m = time.strftime('%M',time.localtime())
    d = time.strftime('%a',time.localtime())

def get_cookie(user,passwd):
    global cookie
    preq = urllib2.Request(lurl)
    pres = urllib2.urlopen(req1)
    html = pres.read()
    token = re.search(r'LT\S+cn',html).group()
    pcookie = re.search(r'JSESSIONID=\S+',str(pres.info().headers)).group()
    data ='lt='+token+'&execution=e1s1&j_pcClient=&_eventId=submit&isApplyed=false&registerSourceUrl=&registerSource=&registerDataSource=&username='+user+'&password='+passwd
    req = urllib2.Request(lurl)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('Cookie',pcookie)]
    try:
        res = opener.open(lurl,data=data,timeout=10)
    except urllib2.URLError:
        print '[ERROR]Please retry later'
    try:
        cookie = re.search(r'ETEAMSID=\w+',str(cj)).group()+';'+re.search(r'JSESSIONID=\w+',str(cj)).group()+';'+re.search(r'WEBID=\w+',str(cj)).group()
        print '[INFO]Login succeed, your cookie is: '+cookie
    except AttributeError:
        print '[ERROR]None cookie recived, please check your username and passwod'
        sys.exit(2)


def keep_seesion():
    req = urllib2.Request(kurl)
    req.add_header('Cookie',cookie)
    req.add_header('X-Requested-With','XMLHttpRequest')
    try:
        res = urllib2.urlopen(req,timeout=5).read()
        msg = res.find('actionMsg')
        if msg > -1:
            print res
    except:
        time.sleep(10)
        keep_live()

def check_in():
    print 'Time for checkin'
    req = urllib2.Request(curl)
    req.add_header("Cookie",cookie)
    req.add_header("Content-Type","application/json")
    data = json.dumps({"type":"CHECKIN"})
    try:
        res = urllib2.urlopen(req,data=data,timeout=5).read()
        print res
        smsg = res.find('签到成功')
        fmsg = res.find('签到失败')
        if smsg > -1:
            logging.info('签到成功')
        elif fmsg > -1:
            logging.warning('签到失败,原因:'+res)
    except:
        time.sleep(10)
        check_in()

def check_out():
    print 'Time for checkout'
    req = urllib2.Request(curl)
    req.add_header("Cookie",cookie)
    req.add_header("Content-Type","application/json")
    data = json.dumps({"type":"CHECKOUT"})
    try:
        res = urllib2.urlopen(req,data,timeout=5).read()
        print res
        smsg = res.find('签退成功')
        fmsg = res.find('签退失败')
        if smsg > -1:
            logging.info('签退成功')
        elif fmsg > -1:
            logging.warning('签退失败,原因:'+res)
    except:
        time.sleep(10)
        check_out()

def check_time():
    while True:
        get_time()
        if d not in ('Sat','Sun'):
            try:
                ih = intime.split(':')[0]
                im = intime.split(':')[1]
                oh = outime.split(':')[0]
                om = outime.split(':')[1]
            except Exception as e:
                print '[ERROR]Wrong format of time'
                break
            if h == 0 and m == 30:
                keep_seesion()
                time.sleep(60)
            elif h == ih and m == im:
                check_in()
                time.sleep(60)
            elif h == oh and m == om:
                check_out()
                time.sleep(60)
        else:
            time.sleep(60)
            check_time()
        time.sleep(60)

def main(argv):
    print banner
    print usage
    try:
        opts, args = getopt.getopt(argv,"-h-i:-o:-u:-p:")
    except  getopt.GetoptError:
        print '[ERROR]Please check your argument and usage'
        sys.exit(2)
    for opt, arg in opts:
        global intime
        global outime
        global user
        global passwd
        if opt == '-h':
            print help
            sys.exit()
        elif opt =='-i':
            intime = arg
        elif opt == '-o':
            outime = arg
        elif opt == '-u':
            user = arg
        elif opt == '-p':
            passwd = arg
    try:
        print 'Running...\nCheckin at '+intime+'\nCheckout at '+outime
    except NameError:
        print '[ERROR]Please check your argument and usage'
        sys.exit(2)
    try:
        get_cookie(user,passwd)
    except NameError:
        print '[ERROR]Please check your argument and usage'
        sys.exit(2)
    check_time()

if __name__ == '__main__':
    main(sys.argv[1:])
