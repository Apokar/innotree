#!/usr/bin/python
# -*- coding: utf-8 -*-
# author : HuaiZ
# first edit : 2017-11-2
# 爬取 公司详情 和 融资信息
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
    detag = detag.replace('{', '')
    detag = detag.replace('}', '')
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
            proxies = get_proxy()
            req = requests.get(html, headers=head, proxies=proxies, timeout=10, verify=False)
            # req = requests.get(html, headers=head, verify=False)

            if req.text.__contains__('{"code":1,"msg":"error"}'):
                print 'error with code:1'
                continue
            elif req.text.__contains__('403 Forbidden'):
                print '403 Forbidden'
                continue
            else:
                # print req.text
                return req.text
                break

        except Exception, e:
            print 'error with get_parse : ' + str(e)
            continue


def get_html_from_db():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
    cursor = conn.cursor()
    old_urls = []
    corp_urls = []
    real_urls = []
    cursor.execute('select url from innotree_company_detailInfo')
    old = cursor.fetchall()

    for y in range(0, len(old)):
        old_urls.append(old[y][0])

    cursor.execute('select company_url from innotree_company_baseInfo')
    data = cursor.fetchall()

    for x in range(0, len(data)):
        corp_urls.append(data[x][0])

    for x in corp_urls:
        if x not in old_urls:
            real_urls.append(x)
    return real_urls


def parse_htmls(html):
    while True:
        try:
            # print html
            com_name = re.findall('<span>公司中文名:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
            print com_name

            com_capital = \
            re.findall('<td>[^<]*<span>注册资本:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
            print com_capital

            com_address = \
            re.findall('<td>[^<]*<span>注册地址:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
            print com_address

            legal_person = \
            re.findall('<td>[^<]*<span>法人代表:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
            print legal_person

            create_time = \
            re.findall('<td>[^<]*<span>成立时间:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[0]
            print create_time

            contact_info = \
            re.findall('<td>[^<]*<span>官方联系方式:[^<]*</span>[^<]*</td>[^<]*<td>[^<]*<span>([^<]*)</span>', html)[
                0]
            print contact_info

            brief = re.findall('<p class="de_170822_d01_d02_p[^<]*">([^<]*)</p>', html)[0]
            print brief

            return [
                com_name,
                com_capital,
                com_address,
                legal_person,
                create_time,
                contact_info,
                detag(brief),
                str(datetime.datetime.now()),
                str(datetime.datetime.now())[:10]

            ]
            break
        except Exception, e:
            print 'error in parse_htmls : ' + str(e)
            break


def get_rongzi(html):
    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
    cursor = conn.cursor()

    soup = BeautifulSoup(html, 'lxml')
    company_name = re.findall('<head>[^<]*<title>([^<]*)</title>', soup.encode('utf8'))[0]

    rongzi = soup.select('body > div > div.de_170822_con > div:nth-of-type(5) > div')[0]
    tr = rongzi.select('tr')

    print '-------'
    print len(tr)
    for i in range(len(tr)):
        span_part = re.findall('<span.*?>(.*?)</span>', str(tr[i]))
        round = re.findall('<span><span class="">(.*?)</span></span>', str(tr[i]))
        href = re.findall('a href="(.*?)"', str(tr[i]))[0]
        a_text = re.findall('<a href=".*?">(.*?)</a>', str(tr[i]), re.M)

        for x in range(len(a_text)):
            print detag(company_name)
            print span_part[0]
            print round[0]
            print span_part[2]
            print href
            print detag(a_text[x])
            cursor.execute('insert into innotree_company_rongziInfo values ("%s","%s","%s","%s","%s","%s","%s","%s")' %

                           (detag(company_name),
                            span_part[0],
                            round[0],
                            span_part[2],
                            href,
                            detag(a_text[x]),
                            str(datetime.datetime.now()),
                            str(datetime.datetime.now())[:10]
                            ))
            conn.commit()


def main():
    while True:
        try:
            conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
            cursor = conn.cursor()

            company_urls = get_html_from_db()
            for html in company_urls:
                print 'parsing :  ' + html
                content = get_parse(html)
                cursor.execute(
                    'insert into innotree_company_detailInfo values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % tuple(
                        [html] + parse_htmls(content.encode('utf-8')))
                )
                conn.commit()
            break
        except Exception, e:
            print '***********' + str(e)
            if str(e).find('TypeError: can only concatenate list (not "NoneType") to list'):
                print '>>>>>>>  TypeError'
            continue


# def main():
#     while True:
#         try:
#             conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
#             cursor = conn.cursor()
#
#             html = 'https://www.innotree.cn/inno/company/14429797997829751781.html'
#             content = get_parse(html)
#
#             cursor.execute(
#                 'insert into innotree_company_detailInfo values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % tuple(
#                     [html] + parse_htmls(content.encode('utf-8')))
#             )
#
#             conn.commit()
#             break
#         except Exception, e:
#             print '***********' + str(e)
#             if str(e).find('TypeError: can only concatenate list (not "NoneType") to list'):
#                 print '>>>>>>>  TypeError'
#             continue


if __name__ == '__main__':
    main()


    # TypeError: can only concatenate list (not "NoneType") to list
