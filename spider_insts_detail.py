#!/usr/bin/python
# -*- coding: utf-8 -*-
# author : HuaiZ
# first edit : 2017-11-6
# 爬取 机构

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import requests
import time
import re
import urllib
import urllib3
import json
import MySQLdb
import datetime
import random
import threading
from bs4 import BeautifulSoup

urllib3.disable_warnings()

from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


head = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Connection': 'keep-alive',
    'Cookie': '_user_identify_=6a3b2c74-d646-3e65-880e-afe2ea04ad40; uID=450357; sID=1a308a5397129f02ac3852748615a9a1; JSESSIONID=aaaFqY4uIFmDK6wwQfW9v; Hm_lvt_37854ae85b75cf05012d4d71db2a355a=1509329421,1509349143,1509414056,1509503306; Hm_lpvt_37854ae85b75cf05012d4d71db2a355a=1509525109',
    'Host': 'www.innotree.cn',
    'Referer': 'https://www.innotree.cn/inno/database/totalDatabase',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


def detag(html):
    detag = re.subn('<[^>]*>', ' ', html)[0]
    detag = re.subn('\\\\u\w{4}', ' ', detag)[0]
    detag = detag.replace('"', '')
    detag = detag.replace(' ', '')
    detag = detag.replace('\n', '')
    detag = detag.replace('\t', '')

    return detag


def get_proxy():
    proxy_list = list(set(urllib.urlopen(
        'http://60.205.92.109/api.do?name=3E30E00CFEDCD468E6862270F5E728AF&status=1&type=static').read().split('\n')[
                          :-1]))
    index = random.randint(0, len(proxy_list) - 1)
    current_proxy = proxy_list[index]
    print "NEW PROXY:\t%s" % current_proxy
    proxies = {"http": "http://" + current_proxy, "https": "http://" + current_proxy, }
    return proxies


def get_parse(html):
    while True:
        try:
            # proxies = get_proxy()
            # req = requests.get(html, headers=head, proxies=proxies, timeout=10, verify=False)
            req = requests.get(html, headers=head, verify=False)

            if req.text.__contains__('{"code":1,"msg":"error"}'):
                print 'error with code:1'
                continue
            elif req.text.__contains__('403 Forbidden'):
                print '403 Forbidden'
                continue
            else:
                return req.text
                break

        except Exception, e:
            print 'error with get_parse : ' + str(e)
            continue


def get_html_from_db():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
    cursor = conn.cursor()
    old_urls = []
    insts_urls = []
    real_urls = []
    cursor.execute('select url from innotree_insts_detailInfo')
    old = cursor.fetchall()
    for y in range(0,len(old)):
        old_urls.append(old[y][0])

    cursor.execute('select insts_url from innotree_insts_baseInfo')
    data = cursor.fetchall()

    for x in range(0, len(data)):
        insts_urls.append(data[x][0])

    for x in insts_urls:
        if x not in old_urls:
            real_urls.append(x)
    return real_urls


def parse_htmls(html):

    print html
    insts_name = re.findall('<span>机构中文名:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
    print insts_name
    type = re.findall('<span>机构类型:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
    print type
    insts_Eng_name = re.findall('<span>机构英文名:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
    print insts_Eng_name
    insts_address = re.findall('<span>注册地区:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
    print insts_address
    create_time = re.findall('<span>成立时间:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
    print create_time
    backup = re.findall('<span>是否备案:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
    print backup
    organization_form = re.findall('<span>组织形式:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
    print organization_form
    management_capital = re.findall('<span>管理资本:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
    print management_capital

    brief = re.findall('<p class="de_170822_d01_d02_p[^<]*">(.*?)</p>', html, re.S)[0]
    print detag(brief)
    # return [
    #     insts_name,
    #     type,
    #     insts_address,
    #     insts_Eng_name,
    #     create_time,
    #     backup,
    #     organization_form,
    #     management_capital,
    #     detag(brief),
    #     str(datetime.datetime.now()),
    #     str(datetime.datetime.now())[:10]
    #
    # ]



# def main():
#     while True:
#         try:
#
#             conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
#             cursor = conn.cursor()
#
#             insts_urls = get_html_from_db()
#             for html in insts_urls:
#                 print 'parsing :  ' + html
#                 content = get_parse(html)
#                 cursor.execute(
#                     'insert into innotree_insts_detailInfo values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % tuple(
#                         [html] + parse_htmls(content.encode('utf-8')))
#                 )
#                 conn.commit()
#             break
#         except Exception,e:
#             if str(e).find('TypeError: can only concatenate list (not "NoneType") to list')>1:
#                 print 'error in main 1 : ' + str(e)
#                 continue
#             else:
#                 print 'error in main 2 : ' + str(e)
#                 continue

def main():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
    cursor = conn.cursor()

    html = ' https://www.innotree.cn/inno/institution/detail/5532699318082211286.html'
    content = get_parse(html)
    # print content
    parse_htmls(content.encode('utf8'))

    # cursor.execute(
    #     'insert into innotree_insts_detailInfo values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % tuple(
    #         [html] + parse_htmls(content.encode('utf-8')))
    # )
    # conn.commit()


if __name__ == '__main__':
    main()
