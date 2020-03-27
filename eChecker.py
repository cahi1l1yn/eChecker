#!/usr/bin/python
#-*- coding:utf-8 -*-

'''
----------------------------------------------------
eChecker
Make auto checkin and checkout for eteams
Author: cahi1l1yn
Version:1.6
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
import random
import geocoder

help='''
-h Print this help
-i Set checkin time(%h:%m),random float 0 to 10 min
-o Set checkout time(%h:%m),random float 0 to 10 min
-u Your username of eteams
-p Your password of etaams
-a Set address for checkin and checkout,can be IP or location

'''

banner='''
----------------------------------------------------
eChecker
Make auto checkin and checkout for eteams
Author: cahi1l1yn
Version:1.6
----------------------------------------------------
'''

kurl = 'https://www.eteams.cn/portal/tasks.json?name=%E4%BB%BB%E5%8A%A1&isShow=1&id=2&type=mine&userId=4975080324437330342&_=1584491.27775'
curl = 'https://www.eteams.cn/attendapp/timecard/check.json'
lurl = 'https://passport.eteams.cn/login'
ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.9 Safari/537.36'
usage = "Usage: eChecker.py -i checkin_time(%h:%m) -o checkout_time(%h:%m) -u username -p password -a(optional) IP/location\n"
sys.setrecursionlimit(999999999)


def get_cookie(user,passwd):
    global cookie
    preq = urllib2.Request(lurl)
    pres = urllib2.urlopen(preq)
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
        print '[ERROR]Login fail, retry later'
        time.sleep(60)
        get_cookie(username,passwd)
    try:
        cookie = re.search(r'ETEAMSID=\w+',str(cj)).group()+';'+re.search(r'JSESSIONID=\w+',str(cj)).group()+';'+re.search(r'WEBID=\w+',str(cj)).group()
        print '[INFO]Login succeed, your cookie is:'+cookie
    except AttributeError:
        print '[ERROR]None cookie recived, wrong username or password'
        sys.exit(2)

def keep_session():
    print '[INFO]Checking session'
    req = urllib2.Request(kurl)
    req.add_header('Cookie',cookie)
    req.add_header('X-Requested-With','XMLHttpRequest')
    try:
        res = urllib2.urlopen(req,timeout=5).read()
        msg = res.find('actionMsg')
        if msg > -1:
            print '[WARNING]'+res
            print '[INFO]Now re-login'
            get_cookie(user,passwd)
        else:
            print '[INFO]Seesion alive'
    except:
        time.sleep(10)
        keep_live()

def check_in():
    print '[INFO]Time for checkin'
    req = urllib2.Request(curl)
    req.add_header("Cookie",cookie)
    req.add_header("Content-Type","application/json")
    if stat == '0':
        data = json.dumps({"type":"CHECKIN","checkAddress":addr,"longitude":longi,'latitude':lati})
    elif stat == '1':
        data = json.dumps({"type":"CHECKIN","checkAddress":addr})
    elif stat =='2':
        req.add_header('User-Agent',ua)
        data = json.dumps({"type":"CHECKIN"})
    try:
        res = urllib2.urlopen(req,data=data,timeout=5).read()
        smsg = res.find('签到成功')
        fmsg = res.find('签到失败')
        if smsg > -1:
            print '[INFO]'+time.strftime('%c',time.localtime())+' Checkin succeed'
        elif fmsg > -1:
            print '[WARNING]'+time.strftime('%c',time.localtime())+' Checkin fail:'+res
    except:
        time.sleep(10)
        check_in()

def check_out():
    print '[INFO]Time for checkout'
    req = urllib2.Request(curl)
    req.add_header("Cookie",cookie)
    req.add_header("Content-Type","application/json")
    if stat == '0':
        data = json.dumps({"type":"CHECKOUT","checkAddress":addr,"longitude":longi,'latitude':lati})
    elif stat == '1':
        data = json.dumps({"type":"CHECKOUT","checkAddress":addr})
    elif stat =='2':
        req.add_header('User-Agent',ua)
        data = json.dumps({"type":"CHECKOUT"})
    try:
        res = urllib2.urlopen(req,data,timeout=5).read()
        smsg = res.find('签退成功')
        fmsg = res.find('签退失败')
        if smsg > -1:
            print '[INFO]'+time.strftime('%c',time.localtime())+' Checkout succeed'
        elif fmsg > -1:
            print '[WARNING]'+time.strftime('%c',time.localtime())+' Checkout fail:'+res
    except:
        time.sleep(10)
        check_out()

def check_time():
    while True:
        ltime = time.strftime('%H:%M',time.localtime()).lstrip('0')
        day = time.strftime('%a',time.localtime())
        s = time.strftime('%S',time.localtime())
        if ltime == '4:30':
            keep_session()
            time.sleep(60)
        elif ltime == intime.lstrip('0') and day not in ('Sat','Sun'):
            keep_session()
            rnd = random.randint(0,600)
            print '[INFO]Checkin after ' + str(int(rnd)/60) + ' Min ' + str(int(rnd)%60) + ' Sec'
            time.sleep(int(rnd))
            check_in()
            time.sleep(60)
        elif ltime == outime.lstrip('0') and day not in ('Sat','Sun'):
            keep_session()
            rnd = random.randint(0,600)
            print '[INFO]Checkout after ' + str(int(rnd)/60) + ' Min ' + str(int(rnd)%60) + ' Sec'
            time.sleep(int(rnd))
            check_out()
            time.sleep(60)
        else:
            if s == '00' :
                time.sleep(60)
            else:
                time.sleep(1)
        check_time()

def get_position(addr):
    global longi
    global lati
    locate = geocoder.arcgis(addr)
    longi = str(locate.latlng[1])
    lati = str(locate.latlng[0])

def main(argv):
    print banner
    print usage
    try:
        opts, args = getopt.getopt(argv,"-h-i:-o:-u:-p:-a:")
    except  getopt.GetoptError:
        print '[ERROR]Please check your argument and usage'
        sys.exit(2)
    for opt, arg in opts:
        global intime
        global outime
        global user
        global passwd
        global addr
        global stat
        if opt == '-h':
            print help
            sys.exit(0)
        elif opt =='-i':
            intime = arg
        elif opt == '-o':
            outime = arg
        elif opt == '-u':
            user = arg
        elif opt == '-p':
            passwd = arg
        elif opt == '-a':
            addr = arg
    try:
        time.strptime(intime,'%H:%M')
        time.strptime(outime,'%H:%M')
        print 'Running...\nCheckin at '+intime+' +(0-10 min)\nCheckout at '+outime+' +(0-10 min)'
    except BaseException:
        print '[ERROR]Error format of time'
        sys.exit(2)
    try:
        stat = '0'
        print '[INFO]Check address is:'+addr
        try:
            get_position(addr)
            print '[INFO]Position is:['+longi+','+lati+']'
        except BaseException:
            stat = '1'
            print '[INFO]Position is:[Can not get position]'
            pass    
    except BaseException: 
        stat = '2'
        pass
    try:
        get_cookie(user,passwd)
    except NameError:
        print '[ERROR]Please check your username and password'
        sys.exit(2)
    check_time()

if __name__ == '__main__':
    main(sys.argv[1:])
