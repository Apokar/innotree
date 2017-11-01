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
    'Cookie': '_user_identify_=6a3b2c74-d646-3e65-880e-afe2ea04ad40; uID=450357; sID=1a308a5397129f02ac3852748615a9a1; JSESSIONID=aaaFqY4uIFmDK6wwQfW9v; Hm_lvt_37854ae85b75cf05012d4d71db2a355a=1509329421,1509349143,1509414056,1509503306; Hm_lpvt_37854ae85b75cf05012d4d71db2a355a=1509525109',
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
            req = requests.get(html, headers=head, verify=False)

            if req.text.__contains__('{"code":1,"msg":"error"}'):
                print 'error with code:1'
                continue
            else:
                return req.text
                break

        except Exception, e:
            print 'line 66 : ' + str(e)
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
            url = 'https://www.innotree.cn/inno/search/ajax/getCompanySearchResultV2?query=&areaName=' + urllib.quote(
                areaName) + '&rounds=' + str(x) + '&st=1'
            first_page_lists.append(url)
    return first_page_lists


# 获取--该维度下信息数量 返回页面数
def get_page_num(html):
    company_count = re.findall('"count":(.*?),', html)[0]
    if company_count != 0:
        if int(company_count) % 10 == 0:
            count = int(company_count) / 10
        else:
            count = int(company_count) / 10 + 1
        return count
    else:
        count = 1
        return count


# 获取--各个维度下的所有页面
def get_all_page(count, page):
    all_page_list = []
    for i in range(1, count + 1):
        real_url = page[:-1] + str(i) + '&ps=10&sEdate=-1&sFdate=1&sRound=-1&chainName='
        all_page_list.append(real_url)
    print all_page_list
    return all_page_list



def get_every_page():
    every_page = []
    first_page_lists = get_first_page_lists()
    for page in first_page_lists:
        html = get_parse(page)
        count = get_page_num(html)
        all_page_list = get_all_page(count, page)
        every_page += all_page_list
    return every_page


def get_html():
    existed_htmls = []
    every_page = get_every_page()
    cursor.execute('select htmls from innotree_company_baseInfo ')
    data = cursor.fetchall()

    for x in range(len(data)):
        existed_htmls.append(data[x][0])

    for html in every_page:
        if html not in existed_htmls:
            htmls.append(html)
    return htmls
    # every_page = get_every_page()
    # for html in every_page:
    #     htmls.append(html)
    # return htmls

def main(html):
    # while True:
    #     try:
            conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
            cursor = conn.cursor()

            time.sleep(1)
            print 'getting  : ' + html

            content = get_parse(html)
            j_content = json.loads(content)
            # print j_content
            data = j_content['data']['company']['infos']
            for index in data:
                # 最近融资时间
                idate = index['idate']
                # 公司
                name = index['name']
                # 公司logo
                logo = index['logo']
                # 公司url
                company_url = 'https://www.innotree.cn/inno/company/' + index['ncid'] + '.html'
                # 产品名
                alias = index['alias']
                # 地址
                address = index['address']
                # 轮次
                round = index['round']
                # 成立时间
                edate = index['edate']
                # 融资金额
                amount = index['amount']
                # 投资方
                instsName = index['insts'][0]['instName']

                print name

                cursor.execute(
                    'insert into innotree_company_baseInfo values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % (
                        html,
                        idate,
                        name,
                        logo,
                        company_url,
                        alias,
                        address,
                        round,
                        edate,
                        amount,
                        instsName,
                        str(datetime.datetime.now()),
                        str(datetime.datetime.now())[:10]
                    ))
            conn.commit()
            # break
        # except Exception, e:
        #     print 'error :' + str(e)
        #     continue


if __name__ == '__main__':
    conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="innotree", charset="utf8")
    cursor = conn.cursor()

    # cursor.execute('truncate table innotree_company_baseInfo')
    # conn.commit()
    # cursor.close()
    # conn.close()
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
    print  'len(htmls):  ' + str(len(htmls))
    inner_index = -2

    while True:
        threads = []
        if start_no <= (len(htmls) - thread_num):
            for inner_index in range(0, thread_num):
                print start_no + inner_index

                threads.append(

                    threading.Thread(target=main, args=(htmls[start_no + inner_index],))
                )
        else:

            if (start_no + inner_index) == (len(htmls) - 1):
                break
            else:
                if (len(htmls) - thread_num) < start_no < 2 * abs(len(htmls) - thread_num):
                    for inner_index in range(0, len(htmls) - start_no):
                        print inner_index
                        threads.append(
                            threading.Thread(target=main, args=(htmls[start_no + inner_index],))
                        )

        for t in threads:
            t.setDaemon(True)
            t.start()
        t.join()
        if (start_no + inner_index) == (len(htmls) - 1):
            print u'----------循环结束------------'
            break
        start_no += thread_num
    print 'end'
    # -------多线程-------->





    print '**************插入ok***************'
    # cursor.close()
    # conn.close()
