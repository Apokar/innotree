# -*- coding: utf-8 -*-
# @Time         : 2018/2/9 17:24
# @Author       : Huaiz
# @Email        : Apokar@163.com
# @File         : innotree_company_2.0.py
# @Software     : PyCharm Community Edition
# @PROJECT_NAME : innotree
import json
import sys
import traceback

reload(sys)
sys.setdefaultencoding('utf8')

import urllib3

urllib3.disable_warnings()

import re
import time
import requests
import threading
import random
import datetime
import MySQLdb


def isExist(object_item):
    if object_item:
        return object_item
    else:
        return 'Null'


# 代理部分
def get_proxy():
    proxies = list(set(requests.get(
        "http://60.205.92.109/api.do?name=3E30E00CFEDCD468E6862270F5E728AF&status=1&type=static").text.split('\n')))
    return proxies


def get_parse(url):
    headers = {
        'accept': 'application/json,*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': '_user_identify_=d59f3443-fc42-345f-847d-0a767ab7436a; JSESSIONID=aaai9fYGCVoEa-1F535fw; Hm_lvt_37854ae85b75cf05012d4d71db2a355a=1518168153; Hm_lvt_ddf0d99bc06024e29662071b7fc5044f=1518168153; uID=462601; sID=e9b961efc14e8d25351eb519de4c2dfe; Hm_lpvt_37854ae85b75cf05012d4d71db2a355a=1518170437; Hm_lpvt_ddf0d99bc06024e29662071b7fc5044f=1518170437',
        'Host': 'www.innotree.cn',
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',

    }

    while True:
        try:

            index = random.randint(1, len(proxies) - 1)
            proxy = {"http": "http://" + str(proxies[index]), "https": "http://" + str(proxies[index])}
            print 'Now Proxy is : ' + str(proxy) + ' @ ' + str(datetime.datetime.now())
            response = requests.get(url, timeout=30, proxies=proxy, headers=headers)
            if response.status_code == 200:
                print 'parse correct'
                return response
                break
            else:
                print 'parse error'
                return None
                break
        except Exception, e:

            print e
            if str(e).find('HTTPSConnectionPool') >= 0:
                time.sleep(3)
                continue
            elif str(e).find('HTTPConnectionPool') >= 0:
                time.sleep(3)
                continue
            else:
                return None
                break


def get_product_parse(id):
    product_url = 'https://www.innotree.cn/inno/company/ajax/projectlist?compId=' + id
    product_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': '_user_identify_=d59f3443-fc42-345f-847d-0a767ab7436a; uID=462601; sID=e9b961efc14e8d25351eb519de4c2dfe; JSESSIONID=aaaupM3mL0_-E7T9JV_fw; Hm_lvt_ddf0d99bc06024e29662071b7fc5044f=1518168153,1518170421,1518246493,1518249854; Hm_lvt_37854ae85b75cf05012d4d71db2a355a=1518168153,1518170421,1518246493,1518249854; Hm_lpvt_37854ae85b75cf05012d4d71db2a355a=1518254569; Hm_lpvt_ddf0d99bc06024e29662071b7fc5044f=1518254569',
        'Host': 'www.innotree.cn',
        'Referer': 'https://www.innotree.cn/inno/company/' + id + '.html',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    while True:
        try:

            index = random.randint(1, len(proxies) - 1)
            proxy = {"http": "http://" + str(proxies[index]), "https": "http://" + str(proxies[index])}
            print 'Now Proxy is : ' + str(proxy) + ' @ ' + str(datetime.datetime.now())
            response = requests.get(product_url, timeout=30, proxies=proxy, headers=product_headers)
            if response.status_code == 200:
                print 'parse correct'
                return response
                break
            else:
                print 'parse error'
                return None
                break
        except Exception, e:

            print e
            if str(e).find('HTTPSConnectionPool') >= 0:
                time.sleep(3)
                continue
            elif str(e).find('HTTPConnectionPool') >= 0:
                time.sleep(3)
                continue
            else:
                return None
                break


# 正 则

def re_findall(pattern, html):
    if re.findall(pattern, html):
        return re.findall(pattern, html)
    else:
        return 'N'

def reS_findall(pattern, html):
    if re.findall(pattern, html, re.S):
        return re.findall(pattern, html, re.S)
    else:
        return 'N'


# 清理数据
def detag(html):
    detag = re.subn('<[^>]*>', ' ', html)[0]
    detag = re.subn('\\\\u\w{4}', ' ', detag)[0]
    detag = detag.replace('{', '')
    detag = detag.replace('}', '')
    detag = detag.replace('&nbsp;', '')
    detag = detag.replace(' ', '')
    detag = detag.replace('\n', '')
    detag = detag.replace('\t', '')
    return detag


def splitag(html):
    detag = re.subn('<[^>]*>', '|', html)[0]
    detag = re.subn('\\\\u\w{4}', ' ', detag)[0]
    detag = detag.replace('{', '')
    detag = detag.replace('}', '')
    detag = detag.replace('&nbsp;', '')
    detag = detag.replace(' ', '')
    detag = detag.replace('\n', '')
    detag = detag.replace('\t', '')

    return detag


# 获得中文
def get_chinese(str):
    b = re.compile(u"[\u4e00-\u9fa5]*")
    c = "".join(b.findall(str.decode('utf8')))
    return c


def get_id_fromDB():
    conn = MySQLdb.connect(host="221.226.72.226", port=13306, user="root", passwd="somao1129", db="innotree",
                           charset="utf8")
    cursor = conn.cursor()

    cursor.execute('select company_id from t_innotree_recent_inst_list')
    all_ids = []
    all = cursor.fetchall()
    for x in range(len(all)):
        all_ids.append(all[x][0])

    cursor.execute('select company_id from table_innotree_company_baseinfo')
    old_ids = []
    old = cursor.fetchall()
    for y in range(len(old)):
        old_ids.append(old[y][0])

    need_ids = []
    for need_id in all_ids:
        if need_id not in old_ids:
            need_ids.append(need_id)

    cursor.close()
    conn.close()
    return need_ids


def get_info(id):
    try:
        conn = MySQLdb.connect(host="221.226.72.226", port=13306, user="root", passwd="somao1129", db="innotree",
                               charset="utf8")
        cursor = conn.cursor()

        url = 'https://www.innotree.cn/inno/company/' + id + '.html'
        ct = get_parse(url)

        if ct:

            content = str(ct.text)
            print content
            title = \
                reS_findall('<title>(.*?)</title>', content)[
                    0].decode('utf8')
            print detag(title)[:-4]

            rounds = reS_findall('<span class="mech_170525_nav_h3_s01">(.*?)</span>', content)[0]
            print detag(rounds).replace('(', '').replace(')', '')

            province = re_findall('<a href="/inno/database/totalDatabase\?areasName=(.*?)"', content)[0]
            print detag(province)

            website = re_findall('href="(.*?)" class="mech_170822_nav_d02_a02"', content)[0]
            print website

            tag = re_findall('<a href="/inno/database/totalDatabase\?tagquery=(.*?)"', content)
            tags = '|'
            for x in tag:
                tags += x + '|'
            print tags

            company_name = reS_findall('<span>公司中文名: </span>(.*?)</span>', content)[0]
            print detag(company_name)

            register_address = reS_findall('<span>注册地址: </span>(.*?)</span>', content)[0]
            print detag(register_address)

            create_time = reS_findall('<span>成立时间: </span>(.*?)</span>', content)[0]
            print detag(create_time)

            register_amount = reS_findall('<span>注册资本: </span>(.*?)</span>', content)[0]
            print detag(register_amount)

            legal_representative = reS_findall('<span>法人代表: </span>(.*?)</span>', content)[0]
            print detag(legal_representative)

            official_contact = reS_findall('<span>官方联系方式: </span>(.*?)</span>', content)[0]
            print detag(official_contact)

            company_brief = reS_findall('<h3 class="de_170822_d01_d02_h3">.*?:</h3>(.*?)</p>', content)[0]
            print detag(company_brief)

            cursor.execute(
                'insert into table_innotree_company_baseinfo values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")' % (
                    id
                    , detag(title)[:-4]
                    , detag(rounds).replace('(', '').replace(')', '')
                    , detag(province)
                    , website
                    , tags
                    , detag(company_name)
                    , detag(register_address)
                    , detag(create_time)
                    , detag(register_amount)
                    , detag(legal_representative)
                    , detag(official_contact)
                    , detag(company_brief)
                    , str(datetime.datetime.now())
                    , str(datetime.datetime.now())[:10]
                ))
            # conn.commit()
            print '公司id: ' + id + ' 的基本信息 插入成功 @ ' + str(datetime.datetime.now())

            # ###########融资信息#############
            if content.__contains__('<h3 class="de_170822_d01_h3">融资信息</h3>'):
                finance_info = re.findall('<h3 class="de_170822_d01_h3">融资信息</h3>(.*?)</table>', content, re.S)[0]
                # print finance_info

                finance_num = len(re.findall('<span><span class="">(.*?)</span></span>', finance_info))
                # print finance_num

                for x in range(int(finance_num)):
                    create_time = re_findall('<span>(.*?)</span>', finance_info)[3 * x]

                    rounds = re_findall('<span><span class="">(.*?)</span></span>', finance_info)[x]

                    amount = re_findall('<span>(.*?)</span>', finance_info)[3 * x + 2]

                    inv = splitag(reS_findall('<td>(.*?)</td>', finance_info)[4 * x + 3])

                    print create_time
                    print rounds
                    print amount
                    print inv
                    cursor.execute(
                        'insert into table_innotree_company_finance_info values ("%s","%s","%s","%s","%s","%s","%s")' % (
                            id
                            , create_time
                            , rounds
                            , amount
                            , inv
                            , str(datetime.datetime.now())
                            , str(datetime.datetime.now())[:10]
                        ))
                    # conn.commit()
                print '公司id: ' + id + ' 的融资信息 插入成功 @ ' + str(datetime.datetime.now())

            ############团队信息#############
            if content.__contains__('<h3 class="de_170822_d01_h3">团队信息</h3>'):
                team_info = reS_findall('<h3 class="de_170822_d01_h3">团队信息</h3>(.*?)</table>', content)[0]
                # print team_info

                people_num = len(re_findall('<span class="de_170822_d01_d05_s01">(.*?)</span>', team_info))
                # print people_num

                for x in range(int(people_num)):
                    people_name = re_findall('<span class="de_170822_d01_d05_s01">(.*?)</span>', team_info)[x]

                    position = detag(reS_findall('<span>(.*?)<div class="de_170822_d01_d05_d">', team_info)[x])

                    introduction = detag(reS_findall('<div class="de_170822_d01_d05_d">(.*?)</p>', team_info)[x])

                    print people_name
                    print position
                    print introduction

                    cursor.execute(
                        'insert into table_innotree_company_team_info values ("%s","%s","%s","%s","%s","%s")' % (
                            id
                            , people_name
                            , position
                            , introduction

                            , str(datetime.datetime.now())
                            , str(datetime.datetime.now())[:10]
                        ))
                    # conn.commit()
                print '公司id: ' + id + ' 的团队信息 插入成功 @ ' + str(datetime.datetime.now())

            # ############股东信息#############
            if content.__contains__('<h3 class="de_170822_d01_h3">股东信息</h3>'):
                shareholder_info = re.findall('<div class="de_170822_d01_d04_d01">(.*?)</table>', content, re.S)[0]
                # print shareholder_info

                shareholder_num = len(re.findall('<div class="de_170822_d01_d05_d_01">', shareholder_info))
                # print shareholder_num

                for x in range(int(shareholder_num)):
                    shareholder_name = re_findall('<p>(.*?)</p>', shareholder_info)[x]
                    shareholder_amount = re_findall('<span>(.*?)</span>', shareholder_info)[2 * x]
                    shareholder_proportion = re_findall('<span>(.*?)</span>', shareholder_info)[2 * x + 1]

                    print shareholder_name
                    print shareholder_amount
                    print shareholder_proportion

                    cursor.execute(
                        'insert into table_innotree_company_shareholder_info values ("%s","%s","%s","%s","%s","%s")' % (
                            id
                            , shareholder_name
                            , shareholder_amount
                            , shareholder_proportion
                            , str(datetime.datetime.now())
                            , str(datetime.datetime.now())[:10]
                        ))
                    # conn.commit()
                print '公司id: ' + id + ' 的团队信息 插入成功 @ ' + str(datetime.datetime.now())

            ############产品信息#############
            product_content = get_product_parse(id)
            if product_content:
                p_content = product_content.text
                data = json.loads(p_content)
                product_info = data["data"]
                if product_info == []:
                    print '没有产品信息'
                    pass
                else:
                    print product_info
                    print len(product_info)
                    for x in range(len(product_info)):
                        print product_info[x]['introduction']
                        print product_info[x]['logo']
                        print product_info[x]['sName']
                        print product_info[x]['score']

                        cursor.execute(
                            'insert into table_innotree_company_production_info values ("%s","%s","%s","%s","%s","%s","%s")' % (
                                id
                                , product_info[x]['sName']
                                , product_info[x]['logo']
                                , product_info[x]['score']
                                , product_info[x]['introduction']
                                , str(datetime.datetime.now())
                                , str(datetime.datetime.now())[:10]
                            ))
                        # conn.commit()
                        print '公司id: ' + id + ' 的产品信息 插入成功 @ ' + str(datetime.datetime.now())

    except:
        print traceback.format_exc()



if __name__ == '__main__':
    while True:
        proxies = get_proxy()
        need_ids = get_id_fromDB()

        start_no = 0
        end_no = len(need_ids)
        thread_num = 5
        while start_no < (end_no - thread_num + 1):
            threads = []

            for inner_index in range(0, thread_num):
                threads.append(threading.Thread(target=get_info, args=(need_ids[start_no + inner_index],)))
            for t in threads:
                t.setDaemon(True)
                t.start()
            t.join()
            start_no += thread_num
        print '执行完毕  _@_ '+str(datetime.datetime.now()) + 'sleep 24 hours and run again, don\'t kill me '
        time.sleep(86400)
    # id1 = '245291808249502742'
    # proxies = get_proxy()
    # # id2 = '9172814686291618768'
    # # id3 = '11636707478071503398'  # 没有产品信息的
    # get_info(id1)
