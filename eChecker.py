#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
----------------------------------------------------
eChecker
Make auto checkin and checkout for eteams
Author: cahi1l1yn
Version:0.9
--------------------------------------------------
'''

import getopt
import sys
import urllib2
import time
import logging
import json

help='''
eChecker
Usage: eChecker.py -i [checkin_time](%hh:%mm) -o [checkout_time](%hh:%mm) -c [Cookie]('cookie_string')

-h Print this help
-i Set checkin time(%hh:%mm)
-o Set checkout time(%hh:%mm)
-c Set your cookie
'''
banner='''
----------------------------------------------------
eChecker
Make auto checkin and checkout for eteams
Author: cahi1l1yn
Version:0.9
----------------------------------------------------
'''
global cookie
global intime
global outime
kurl = 'https://www.eteams.cn/portal/tasks.json?name=%E4%BB%BB%E5%8A%A1&isShow=1&id=2&type=mine&userId=4975080324437330342&_=1584491917775'
curl = 'https://www.eteams.cn/attendapp/timecard/check.json'
agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36'
usage = "Usage: eChecker.py -i [checkin_time](%hh:%mm) -o [checkout_time](%hh:%mm) -c [Cookie]('cookie_string')\n"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='check.log',
    filemode='a')

def get_time():
    global h,m
    h = time.strftime('%H',time.localtime())
    m = time.strftime('%M',time.localtime())

def keep_seesion():
    req = urllib2.Request(kurl)
    req.add_header('Cookie',cookie)
    req.add_header('X-Requested-With','XMLHttpRequest')
    try:
        res = urllib2.urlopen(req,timeout=5).read()
        msg = res.find('actionMsg')
        if msg > -1:
            logging.warning(res)
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
        try:
            ih = intime.split(':')[0]
            im = intime.split(':')[1]
            oh = outime.split(':')[0]
            om = outime.split(':')[1]
        except Exception as e:
            print 'Error format of time'
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
    time.sleep(60)

def main(argv):
    print banner
    print usage
    try:
        opts, args = getopt.getopt(argv,"-h-i:-o:-c:")
    except  getopt.GetoptError:
        print usage
        sys.exit(2)
    for opt, arg in opts:
        global cookie
        global intime
        global outime
        if opt == '-h':
            print help
            sys.exit()
        elif opt =='-i':
            intime = arg
        elif opt == '-o':
            outime = arg
        elif opt == '-c':
            cookie = arg
    print 'Running...\nCheckin at '+intime+'\nCheckout at '+outime
    print 'Your cookie is:\n'+cookie
    check_time()

if __name__ == '__main__':
    main(sys.argv[1:])
