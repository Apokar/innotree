#!/usr/bin/python
# -*- coding: utf-8 -*-
# author : HuaiZ
# first edit : 2017-10-26

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

urllib3.disable_warnings()


def re_findall(pattern, html):
    if re.findall(pattern, html, re.S):
        return re.findall(pattern, html, re.S)
    else:
        return 'N'


def get_proxy():
    proxy_list = list(set(urllib.urlopen(
        'http://60.205.92.109/api.do?name=3E30E00CFEDCD468E6862270F5E728AF&status=1&type=static').read().split('\n')[
                          :-1]))
    index = random.randint(0, len(proxy_list) - 1)
    current_proxy = proxy_list[index]
    print "NEW PROXY:\t%s" % current_proxy
    proxies = {"http": "http://" + current_proxy, "https": "http://" + current_proxy, }
    return proxies


head = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Connection': 'keep-alive',
    'Cookie': '_user_identify_=6a3b2c74-d646-3e65-880e-afe2ea04ad40; JSESSIONID=aaacYZNUM8Bqj8wwzBw9v; Hm_lvt_37854ae85b75cf05012d4d71db2a355a=1508917351,1508919101,1508983546,1508984230; Hm_lpvt_37854ae85b75cf05012d4d71db2a355a=1508997943',
    'Host': 'www.innotree.cn',
    'Referer': 'https://www.innotree.cn/inno/database/totalDatabase',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

htmls = []


# 解析--页面
def get_parse(html):
    while True:
        try:
            proxies = get_proxy()
            req = requests.get(html, headers=head, proxies=proxies, timeout=10, verify=False)
            # req = requests.get(html, headers=head, verify=False)
            return req.text
            break
        except Exception, e:
            print str(e)
            continue


# 获取--各个维度的第一页
def get_first_page_lists():
    first_page_lists = []
    # area = ['北京市', '天津市', '上海市', '重庆市', '河北省', '山西省', '内蒙古自治区辽宁省', '吉林省', '黑龙江省', '江苏省', '浙江省', '安徽省', '福建省', '江西省',
    #         '山东省', '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区海南省', '四川省', '贵州省', '云南省', '西藏自治区陕西省', '甘肃省', '青海省',
    #         '宁夏回族自治区新疆维吾尔自治']
    # rounds = ['1-2', '3-4-5-6-7-8', '9-10-11-12-13-14', '15-16-17-18-19', '20-21', '30', '40', '50', '60']
    area = ['北京市']
    rounds = ['60']

    for areaName in area:
        for x in rounds:
            url = 'https://www.innotree.cn/inno/search/ajax/getInstitutionSearchResultV2?query=&areaName=' + urllib.quote(
                areaName) + '&rounds=' + str(x) + '&st=1'
            first_page_lists.append(url)
    return first_page_lists


# 获取--该维度下信息数量 返回页面数
def get_page_num(html):
    insti_count = re_findall('"count":(.*?),', html)[0]
    if int(insti_count) % 10 == 0:
        count = int(insti_count) / 10
    else:
        count = int(insti_count) / 10 + 1
    return count


# 获取--各个维度下的所有页面
def get_all_page(count, page):
    all_page_list = []

    for i in range(1, count + 1):
        real_url = page[:-1] + str(i) + '&ps=10&sInum=1&sEnum=-1&sEdate=-1'
        all_page_list.append(real_url)
    print all_page_list
    return all_page_list


def get_every_page():
    every_page = []
    first_page_lists = get_first_page_lists()
    # print first_page_lists
    for page in first_page_lists:
        html = get_parse(page)
        count = get_page_num(html)
        all_page_list = get_all_page(count, page)
        every_page += all_page_list
    return every_page


def get_html():
    every_page = get_every_page()
    for html in every_page:
        htmls.append(html)
    return htmls


def main(html):
    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
    cursor = conn.cursor()

    time.sleep(1)
    print 'test: ' + html
    content = get_parse(html)
    j_content = json.loads(content)
    data = j_content['data']['inst']['infos']
    for index in data:
        # 组织名
        name = index['name']
        # 组织logo
        logo = index['logo']
        # id
        insts_id = index['instid']
        # 组织url
        insts_url = 'https://www.innotree.cn/inno/institution/detail/' + index['instid'] + '.html'
        # 机构简称
        alias = index['alias']
        # 投资笔数
        investCount = index['investCount']
        # 退出笔数
        exitCount = index['exitCount']
        # 投资类型
        investType = index['investType']
        # 成立时间
        creatDate = index['creatDate']
        # 管理基金
        mainFundName = index['mainFundName']

        print name

        # print idate, name, logo, company_url, alias, address, round, edate, amount, instsName
        cursor.execute(
            'insert into innotree_insts_baseInfo values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % (

                name,
                logo,
                insts_id,
                alias,
                insts_url,
                investCount,
                exitCount,
                investType,
                creatDate,
                mainFundName,
                str(datetime.datetime.now()),
                str(datetime.datetime.now())[:10]
            ))
    conn.commit()


if __name__ == '__main__':
    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
    cursor = conn.cursor()

    cursor.execute('truncate table innotree_insts_baseInfo')
    conn.commit()
    cursor.close()
    conn.close()
    # <-------单线程--------

    # htmls = get_html()
    # print  len(htmls)
    # for html in htmls:
    #     main(html)
    # -------单线程-------->

    # <-------多线程--------
    thread_num = 3
    start_no = 0

    htmls = get_html()
    print  len(htmls)
    while True:
        threads = []
        if start_no <= (len(htmls) - thread_num):
            for inner_index in range(0, thread_num):
                print start_no + inner_index

                threads.append(

                    threading.Thread(target=main, args=(htmls[min(start_no + inner_index, len(htmls) - 1)],))
                )
        else:
            if (start_no + inner_index) == (len(htmls) - 1):
                break
            else:
                time.sleep(2)
                if (len(htmls) - thread_num) < start_no < 2 * (len(htmls) - thread_num):
                    for inner_index in range(0, len(htmls) - start_no):
                        print start_no + inner_index
                        threads.append(
                            threading.Thread(target=main, args=(htmls[start_no + inner_index],))
                        )
        for t in threads:
            t.setDaemon(True)
            t.start()
        t.join()
        if (start_no + inner_index) == (len(htmls) - 1):
            print '循环结束'
            break
        start_no += thread_num
    print 'end'
    # -------多线程-------->
    print '--------------插入ok----------------'
    # cursor.close()
    # conn.close()
