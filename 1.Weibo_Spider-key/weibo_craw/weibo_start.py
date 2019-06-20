# -*- coding:utf-8 -*-
import sys

sys.path.append("..")
import time
import requests
from bs4 import BeautifulSoup
from tools.Date_Process import time_process
from tools.Emoji_Process import filter_emoji
from tools.Mysql_Process import mysqlHelper
from tools import Cookie_Process
from tools.Mysql_Process import get_db

url_template = 'https://weibo.cn/{}?page={}'  # 要访问的微博搜索接口URL
flag = 0
"""抓取关键词某一页的数据"""


def fetch_weibo_data(wb_userid, wb_username, page_id):
    cookie = Cookie_Process.read_cookie()  # 获取文件中存储的cookie
    cookies = {
        "Cookie": cookie}

    # 通过' https://weibo.cn/%d '网站获取用户微博的信息
    url_weibo = "https://weibo.cn/%s?page=%d" % (wb_userid, page_id)
    r_weibo = requests.get(url_weibo, cookies=cookies)
    soup_weibo = BeautifulSoup(r_weibo.text, 'lxml')

    all_contents = soup_weibo.select('.c')[1:-2]

    wb_count = 0
    mblog = []  # 保存处理过的微博

    for card in all_contents:
        wb_id = str(card.get('id')).split("_")[1]
        wb_content = filter_emoji(card.select_one('.ctt').text)  # 微博内容

        temp_href = card.select('a')
        for href in temp_href:
            if 'comment' in href.get('href') and '原文评论' not in href.text:
                wb_commentnum = href.text[3:-1]

            if 'attitude' in href.get('href'):
                wb_likenum = href.text[2:-1]

            if 'repost' in href.get('href'):
                wb_forwardnum = href.text[3:-1]

        wb_createtime = time_process(card.select_one('.ct').text.split('\xa0')[0])  # 微博内容

        print('用户名：' + wb_username)
        print('用户ID：' + wb_userid)
        print('微博ID：' + wb_id)
        print('微博内容：' + wb_content)
        print('微博评论数：' + wb_commentnum)
        print('微博点赞数：' + wb_likenum)
        print('微博转发数：' + wb_forwardnum)
        print('微博创建时间：' + wb_createtime)
        print('------------------------------\n')

        blog = {'wb_userid': wb_userid,  # 生成一条微博记录的列表
                'wb_username': wb_username,
                'wb_id': wb_id,
                'wb_content': wb_content,
                'wb_createtime': wb_createtime,
                'wb_forwardnum': wb_forwardnum,
                'wb_commentnum': wb_commentnum,
                'wb_likenum': wb_likenum
                }
        mblog.append(blog)
        wb_count = wb_count + 1  # 表示此页的微博数
    global flag
    if (wb_count > 0):
        print("---------- 第%s页微博爬取完成 ---------- " % page_id + "当前页微博数：" + str(wb_count))
        flag = 0
    else:
        flag = 1
        print("********** 第%s页微博开始被反爬，程序自动睡眠5秒后进行爬取...... " % page_id)
        time.sleep(5)
    print()
    print()
    return mblog


"""抓取关键词多页的数据"""


def fetch_pages(user_id):
    cookie = Cookie_Process.read_cookie()  # 获取文件中存储的cookie
    cookies = {
        "Cookie": cookie}

    # 通过' https://weibo.cn/%d '网站微博第一页获取用户的用户名和总页数
    url_user = "https://weibo.cn/%s?page=%d" % (user_id, 1)
    r_user = requests.get(url_user, cookies=cookies)
    soup_user = BeautifulSoup(r_user.text, 'lxml')

    # 判断用户是否发表了微博，如没有，则返回
    panduan_weibo = soup_user.select_one('.tc').text[3:-1]
    if panduan_weibo == '0':
        print('此用户微博数量为0！')
        return

    user_contents = soup_user.select_one('.ut').select('.ctt')
    temp_user = user_contents[0].text.split()
    wb_username = temp_user[0]  # 获取微博用户名
    # print(wb_username)
    try:
        page_num = int(soup_user.select_one('.pa').text.split()[1].split('/')[1][:-1])  # 获取微博总页数
        print('--------- 微博总页数为：' + str(page_num) + ' ---------\n')
    except Exception as e:
        page_num = 1

    mblogs = []  # 此次时间单位内的搜索全部结果先临时用列表保存，后存入数据库
    page_id = 1
    while page_id <= page_num:
        try:
            mblogs.extend(fetch_weibo_data(user_id, wb_username, page_id))  # 每页调用fetch_data函数进行微博信息的抓取
            if (flag == 1):
                continue

        except Exception as e:
            print(e)
        if (page_id % 50 == 0):  # 每多少条数据执行一次 提交 插入数据库操作
            # 保存到mysql数据库
            mh = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
            sql = "insert into user_weibo(wb_userid,wb_username,wb_id,wb_content,wb_createtime,wb_forwardnum,wb_commentnum,wb_likenum) values(%s,%s,%s,%s,%s,%s,%s,%s)"
            mh.open();
            for i in range(len(mblogs)):
                mh.cud(sql, (mblogs[i]['wb_userid'], mblogs[i]['wb_username'], mblogs[i]['wb_id'],
                             filter_emoji(mblogs[i]['wb_content']),
                             mblogs[i]['wb_createtime'], mblogs[i]['wb_forwardnum'], mblogs[i]['wb_commentnum'],
                             mblogs[i]['wb_likenum']))
            mh.tijiao();
            mh.close()
            mblogs = []  # 提交数据库之后将列表清空
        page_id = page_id + 1
    if len(mblogs) > 0:  # 将余下的数据提交数据库
        # 保存到mysql数据库
        mh = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
        sql = "insert into user_weibo(wb_userid,wb_username,wb_id,wb_content,wb_createtime,wb_forwardnum,wb_commentnum,wb_likenum) values(%s,%s,%s,%s,%s,%s,%s,%s)"
        mh.open();
        for i in range(len(mblogs)):
            mh.cud(sql, (
            mblogs[i]['wb_userid'], mblogs[i]['wb_username'], mblogs[i]['wb_id'], filter_emoji(mblogs[i]['wb_content']),
            mblogs[i]['wb_createtime'], mblogs[i]['wb_forwardnum'], mblogs[i]['wb_commentnum'],
            mblogs[i]['wb_likenum']))
        mh.tijiao();
        mh.close()


if __name__ == '__main__':
    Cookie_Process.write_cookie()
    user_id = input("请输入要搜索的用户ID：")

    time_start = time.time()
    fetch_pages(user_id)
    time_end = time.time()

    print('本次操作数据全部爬取成功，爬取用时秒数:', (time_end - time_start))
