#!/usr/bin/python
# -*- coding: utf-8 -*-
# author : HuaiZ
# first edit : 2017-10-26

import requests
import re
import urllib
import urllib3

urllib3.disable_warnings()


def re_findall(pattern, html):
    if re.findall(pattern, html, re.S):
        return re.findall(pattern, html, re.S)
    else:
        return 'N'


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


# 解析--页面
def get_parse(html):
    req = requests.get(html, headers=head, verify=False)
    return req.text


# 获取--各个维度的第一页
def get_first_page_lists():
    first_page_lists = []
    area = ['北京市', '天津市', '上海市', '重庆市', '河北省', '山西省', '内蒙古自治区辽宁省', '吉林省', '黑龙江省', '江苏省', '浙江省', '安徽省', '福建省', '江西省',
            '山东省', '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区海南省', '四川省', '贵州省', '云南省', '西藏自治区陕西省', '甘肃省', '青海省',
            '宁夏回族自治区新疆维吾尔自治']
    rounds = ['1-2', '3-4-5-6-7-8', '9-10-11-12-13-14', '15-16-17-18-19', '20-21', '30', '40', '50', '60']
    for areaName in area:
        for x in rounds:
            url = 'https://www.innotree.cn/inno/search/ajax/getCompanySearchResultV2?query=&areaName=' + urllib.quote(
                areaName) + '&rounds=' + str(x) + '&st=1'
            first_page_lists.append(url)
    return first_page_lists


# 获取--该维度下信息数量 返回页面数
def get_first_page_num(html):
    company_count = re_findall('"count":(.*?),', html)[0]
    count = int(company_count) / 10 + 1
    return count


# 获取--各个维度下的所有页面
def get_all_page(count, first_page_lists):
    all_page_list = []
    for i in range(1, count + 1):
        for url in first_page_lists:
            real_url = url[:-1] + str(i) + '&ps=10&sEdate=-1&sFdate=1&sRound=-1&chainName='
            all_page_list.append(real_url)
    return all_page_list


# 解析--列表页信息
def parse_first_page(html):
    logo = re_findall('"logo":"(.*?)"', html)[0]
    print logo
    product_name = re_findall('"alias":"(.*?)",', html)[0]
    print product_name
    cid = re_findall('"ncid":"(.*?)",', html)[0]
    print cid
    last_time_of_financing = re_findall('"idate":"(.*?)",', html)[0]
    print last_time_of_financing
    address = re_findall('"address":"(.*?)",', html)[0]
    print address
    edate = re_findall('"edate":"(.*?)",', html)[0]
    print edate
    round = re_findall('"round":(.*?)},', html)[0]
    print round
    amount = re_findall('"amount":"(.*?)",', html)[0]
    print amount
    investor = re_findall('"instName":"(.*?)",', html)[0]
    print investor
    company_count = re_findall('"count":(.*?),', html)[0]
    print company_count


if __name__ == '__main__':
    first_page_lists = get_first_page_lists()
    for page in first_page_lists:
        html = get_parse(page)
        count = get_first_page_num(html)
        all_page_list = get_all_page(count, first_page_lists)
        print all_page_list
