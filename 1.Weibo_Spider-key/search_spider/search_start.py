# -*- coding:utf-8 -*-
import sys
import re
import os
import codecs
import json
import time
import requests
from bs4 import BeautifulSoup
from tools.Date_Process import time_process
from tools.Number_Process import num_process
from tools.OutPut import generate_xlsx
from search_spider.hour_slice import hour_slice
# from tools.Mysql_Process import get_db
from tools.Emoji_Process import filter_emoji
# from tools.Mysql_Process import mysqlHelper
"""
2019.4.28 coded by henry
输入关键字和起止时间（时间格式：2019.4.1.18），爬取微博数据
"""

sys.path.append("..")
url_template = 'https://s.weibo.com/weibo?q={}&typeall=1&suball=1&timescope=custom:{}:{}&Refer=g&page={}'  # 要访问的微博搜索接口URL
exclude_word = ["#", "@", "收起全文", "微博视频", "网页链接"]


def fetch_weibo_data(keyword, start_time, end_time, page_id, page_num):
    """
    根据关键字，起止时间以及页面id进行数据爬取, 返回由[dict…]构成
    """
    # resp = requests.get(url_template.format(keyword, start_time, end_time, page_id))

    mycookie = "SINAGLOBAL=3496136235056.4463.1541040811587; UM_distinctid=1696c6c69c80-02af6028746f6-172a1c0b-1fa400-1696c6c69ca1f6; _ga=GA1.2.559137983.1556505024; __gads=ID=db7d546fb975d8ef:T=1556505024:S=ALNI_MYoQq9hUNW5AVE9sO2DDIXUhTGjHw; _s_tentry=-; Apache=250591394682.5733.1557325425270; ULV=1557325425387:23:2:1:250591394682.5733.1557325425270:1556698994716; login_sid_t=6d479d40943eab98fb9845c777d62d1b; cross_origin_proto=SSL; _gid=GA1.2.1397000584.1557325685; SSOLoginState=1557365898; wvr=6; webim_unReadCount=%7B%22time%22%3A1557366596423%2C%22dm_pub_total%22%3A2%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A3%2C%22msgbox%22%3A0%7D; crossidccode=CODE-tc-1Hoycs-22O4LF-PQJlitc30i7mOag8e8f8d; ALF=1588902634; SUB=_2A25x1_c8DeThGeNL7FcX9izMzT-IHXVSpW_0rDV8PUNbmtAKLVLwkW9NSPOSAn5FYpCGyj8rg27XhJFWogI6mmyD; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFIE6KsnV1qpcU_7ES.krnN5JpX5KzhUgL.Fo-fS0-cSoz7Soe2dJLoIpvKdgLjIg4ri--ci-z7i-zRi--ciKnpiK.EeK.4e02p; SUHB=0XD1zEIME76fUm; UOR=news.ifeng.com,widget.weibo.com,www.baidu.com"
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
        "cookie": mycookie}

    resp = requests.get(url_template.format(keyword, start_time, end_time, page_id), headers=headers, allow_redirects=True)

    print("微薄url:", resp.url)
    if resp.status_code == 200:
        print("fetch_data爬取状态正常")
    else:
        print("爬取状态异常:", resp.status_code)

    if not resp.raise_for_status():
        print("网页请求无报错")  # 网页请求报错
    else:
        print("网页请求出错：", resp.raise_for_status())
        print("网页请求历史", resp.history)

    soup = BeautifulSoup(resp.text, 'lxml')
    all_contents = soup.select('.card-wrap')                 # card-feed为微博内容
    print("本页微博条数：", len(all_contents))

    wb_count = 0
    mblog = []  # 保存处理过的微博
    for z, card in enumerate(all_contents):
        try:
            mid_in = card.get('mid')
        except:
            break
        if (mid_in is not None):  # 如果微博ID不为空则开始抓取
            wb_username = card.select_one('.txt').get('nick-name')  # 微博用户名
            # print(1, wb_username)
            href = card.select_one('.from').select_one('a').get('href')
            # print(2, href)
            re_href = re.compile('.*com/(.*)/.*')
            # print(3, re_href)
            wb_userid = re_href.findall(href)[0]  # 微博用户ID
            # print(4, wb_userid)

            if len(card.select(".txt")) == 2:
                wb_content = card.select('.txt')[1].text.strip()  # 长篇微博会有<展开全文>
            else:
                wb_content = card.select('.txt')[0].text.strip()  # 微博全文内容
            wb_content = wb_content.replace(" ", "")              # 剔除空格
            # print(5, wb_content)

            wb_place = []

            if len(card.select(".txt")) == 2:
                tag_a = card.select('.txt')[1].select("a")        # 获取所有的a标签，组成list
                if tag_a:
                    for i in range(len(tag_a)):
                        text = tag_a[i].text.strip()

                        if "·" in text:
                            wb_place.append(text[1:])
                else:
                    wb_place = []
            else:
                tag_a = card.select('.txt')[0].select("a")
                if tag_a:
                    for i in range(len(tag_a)):
                        text = tag_a[i].text.strip()

                        if "·" in text:
                            wb_place.append(text[1:])
                else:
                    wb_place = []
            # print(9, wb_place)

            wb_create = card.select_one('.from').select_one('a').text.strip()  # 微博创建时间
            # print(6, wb_create)
            wb_url = 'https:' + str(card.select_one('.from').select_one('a').get('href'))  # 微博来源URL
            # print(7, wb_url)
            wb_id = str(card.select_one('.from').select_one('a').get('href')).split('/')[-1].split('?')[0]  # 微博ID
            # print(8, wb_id)
            wb_createtime = time_process(wb_create)
            # print(9, wb_createtime)
            wb_forward = str(card.select_one('.card-act').select('li')[1].text)  # 微博转发
            # print(10, wb_forward)
            wb_forwardnum = num_process(wb_forward.strip())                      # 微博转发数
            # print(11, wb_forwardnum)
            wb_comment = str(card.select_one('.card-act').select('li')[2].text)  # 微博评论
            # print(12, wb_comment)
            wb_commentnum = num_process(wb_comment)                              # 微博评论数
            # print(12, wb_commentnum)
            wb_like = str(card.select_one('.card-act').select_one('em').text)    # 微博点赞数
            # print(13, wb_like)

            if (wb_like == ''):  # 点赞数的处理
                wb_likenum = '0'
            else:
                wb_likenum = wb_like
            # print(14, wb_likenum)
            blog = {'wb_id': wb_id,  # 生成一条微博记录的列表
                    'wb_username': wb_username,
                    'wb_userid': wb_userid,
                    'wb_content': wb_content,
                    'wb_createtime': wb_createtime,
                    'wb_forwardnum': wb_forwardnum,         # 转发数
                    'wb_commentnum': wb_commentnum,         # 评论数
                    'wb_likenum': wb_likenum,
                    'wb_url': wb_url,
                    'wb_place': wb_place
                    }

            mblog.append(blog)
            wb_count = wb_count + 1  # 表示此页的微博数
            # print(666666)

    print("正在爬取" + str(start_time) + "----第"+ str(page_id)+"页/共" + str(page_num) + "页 ---- 当前页微博数：" + str(wb_count))
    return mblog


def fetch_pages(keyword, start_time, end_time):
    """
    使用beatifulsoul获取网页sorce代码，来获取页码信息，获取页码信息后，使用fetch_weibo_data来循环爬取每个面信息
    返回0（爬取失败） or blogs（爬取成功的list数据）
    """
    mycookie = "SINAGLOBAL=3496136235056.4463.1541040811587; UM_distinctid=1696c6c69c80-02af6028746f6-172a1c0b-1fa400-1696c6c69ca1f6; _ga=GA1.2.559137983.1556505024; __gads=ID=db7d546fb975d8ef:T=1556505024:S=ALNI_MYoQq9hUNW5AVE9sO2DDIXUhTGjHw; _s_tentry=-; Apache=250591394682.5733.1557325425270; ULV=1557325425387:23:2:1:250591394682.5733.1557325425270:1556698994716; login_sid_t=6d479d40943eab98fb9845c777d62d1b; cross_origin_proto=SSL; _gid=GA1.2.1397000584.1557325685; SSOLoginState=1557365898; wvr=6; webim_unReadCount=%7B%22time%22%3A1557366596423%2C%22dm_pub_total%22%3A2%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A3%2C%22msgbox%22%3A0%7D; crossidccode=CODE-tc-1Hoycs-22O4LF-PQJlitc30i7mOag8e8f8d; ALF=1588902634; SUB=_2A25x1_c8DeThGeNL7FcX9izMzT-IHXVSpW_0rDV8PUNbmtAKLVLwkW9NSPOSAn5FYpCGyj8rg27XhJFWogI6mmyD; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFIE6KsnV1qpcU_7ES.krnN5JpX5KzhUgL.Fo-fS0-cSoz7Soe2dJLoIpvKdgLjIg4ri--ci-z7i-zRi--ciKnpiK.EeK.4e02p; SUHB=0XD1zEIME76fUm; UOR=news.ifeng.com,widget.weibo.com,www.baidu.com"
    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36', "cookie": mycookie}

    resp = requests.get(url_template.format(keyword, start_time, end_time, '1'), headers=headers, allow_redirects=False)

    if resp.status_code == 200:
        print("fetch_pages爬取状态正常")
    else:
        print("！！！爬取状态异常:", resp.status_code)

    if not resp.raise_for_status():
        print("网页请求无报错")  # 网页请求报错
    else:
        print("！！！网页请求出错：", resp.raise_for_status())
        print("！！！网页请求历史", resp.history)

    soup = BeautifulSoup(resp.text, 'lxml')

    if str(soup.select_one('.card-wrap').select_one('p').text).startswith('抱歉'):  # 此次搜索条件的判断，如果没有相关搜索结果！退出...
        print("搜索条件无相关结果...")
        return 0
    try:
        page_num = len(soup.select_one('.m-page').select('li'))  # 获取此时间单位内的搜索页面的总数量，
        page_num = int(page_num)
        print(start_time + ' 到 ' + end_time + " 时间单位内搜索结果页面总数为：%d" % page_num)
    except Exception:
        page_num = 1

    mblogs = []
    for page_id in range(page_num):
        page_id += 1
        try:
            mblogs.extend(fetch_weibo_data(keyword, start_time, end_time, page_id, page_num))  # 每页调用fetch_data函数进行微博信息的抓取
        except Exception as e:
            print(e)
    file_path = "../data_store/{}".format(keyword)
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    file_name = "../data_store/{}/{}.json".format(keyword, start_time)

    with codecs.open(file_name, "w") as fw:                         # 每小时数据
        print("数据写入json文件当中")
        json.dump(mblogs, fw, indent=4, ensure_ascii=False)
    return mblogs
    # 保存到mysql数据库
    # mh = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
    # sql = "insert into keyword_weibo(wb_id,wb_username,wb_userid,wb_content,wb_createtime,wb_forwardnum,wb_commentnum,wb_likenum,wb_url,keyword) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    # mh.open();
    # for i in range(len(mblogs)):
    #     mh.cud(sql, (
    #         mblogs[i]['wb_id'], mblogs[i]['wb_username'], mblogs[i]['wb_userid'], filter_emoji(mblogs[i]['wb_content']),
    #         mblogs[i]['wb_createtime'], mblogs[i]['wb_forwardnum'], mblogs[i]['wb_commentnum'], mblogs[i]['wb_likenum'],
    #         mblogs[i]['wb_url'], keyword))
    # mh.tijiao();
    # mh.close()


if __name__ == '__main__':
    # keyword = input("请输入要搜索的关键字：")
    # start_time = input("请输入要查询的开始时间：")
    # end_time = input("请输入要查询的结束时间：")
    #
    keyword = "山竹"
    start_time = "2018.9.14.0"
    end_time = "2018.9.19.0"

    time_start = time.time()
    hour_all = hour_slice(start_time, end_time)             # 提取规范的时间格式，按每小时切分[（开始时间， 结束时间）……]

    datas_list = []
    i = 0
    for i in range(len(hour_all)):

        datas = fetch_pages(keyword, hour_all[i][0], hour_all[i][1])            # 程序主要入口, 开始时间和结束时间

        if datas != 0:
            print(hour_all[i][0] + ' 到 ' + hour_all[i][1] + ' 时间内的数据爬取完成！\n\n')
            datas_list.extend(datas)
        else:
            print("该次查询结果为空\n")

    file_name0 = "../data_store/{}_{}_{}".format(keyword, start_time, end_time)
    with codecs.open(file_name0, "w") as fw:
        print("整体爬取数据写入json文件：", file_name0)
        json.dump(datas_list, fw, indent=4, ensure_ascii=False)

    generate_xlsx(datas_list, file_name0)                                                   # 生成xlsl文件
    print("生成xlsl文件:", file_name0)

    time_end = time.time()
    time_delta = time_end - time_start
    print("用时:"+ str(round(time_delta, 2)) + "秒")
    print("数据爬取顺利完成!!!")
