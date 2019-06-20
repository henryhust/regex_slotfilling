import sys

sys.path.append("..")
import requests
import re
import time
from bs4 import BeautifulSoup
from tools import Cookie_Process
from tools.Emoji_Process import filter_emoji
from tools.Mysql_Process import mysqlHelper
from tools.Mysql_Process import get_db

'''爬取某个用户ID的基本信息'''


def fetch_user_data(user_id, keyword, cookie):
    cookies = {
        "Cookie": cookie}

    try:
        # 通过' https://weibo.cn/%d '网站获取用户的微博数量、关注数和粉丝数
        url_user = "https://weibo.cn/%d" % (user_id)
        r_user = requests.get(url_user, cookies=cookies)
        soup_user = BeautifulSoup(r_user.text, 'lxml')
        user_wbnum = soup_user.select_one('.tc').text
        user_wbnum = re.sub("\D", "", user_wbnum)  # 微博数量
        user_follow = soup_user.select_one('.tip2').select('a')[0].text
        user_follow = re.sub("\D", "", user_follow)  # 关注数量
        user_fan = soup_user.select_one('.tip2').select('a')[1].text
        user_fan = re.sub("\D", "", user_fan)  # 粉丝数量

        all_contents = soup_user.select_one('.ut').select('.ctt')
        if len(all_contents) == 2:
            temp_info = all_contents[0].text.split()
            user_name = temp_info[0]
            user_sex = str(temp_info[1]).split('/')[0]
            user_address = str(temp_info[1]).split('/')[1]
            user_renzheng = '无'
            user_oneword = filter_emoji(all_contents[1].text)

        else:
            temp_info = all_contents[0].text.split()
            user_name = temp_info[0]
            user_sex = str(temp_info[1]).split('/')[0]
            user_address = str(temp_info[1]).split('/')[1]
            user_renzheng = filter_emoji(all_contents[1].text)
            user_oneword = filter_emoji(all_contents[2].text)
        if user_oneword == '':
            user_oneword = '无'
    except Exception as err:
        return

    print('用户ID：' + str(user_id))
    print('用户名：' + user_name)
    print('用户性别：' + user_sex)
    print('用户地址：' + user_address)
    print('用户简介：' + user_oneword)
    print('用户认证：' + user_renzheng)
    print('用户页面的url：' + url_user)
    print('微博数量：' + user_wbnum)
    print('关注数：' + user_follow)
    print('粉丝数：' + user_fan)
    print('关键字：' + keyword)
    print('--------------------------------\n')

    userinfo = []
    user = {'user_id': user_id,  # 生成一条用户信息的列表
            'user_name': user_name,
            'user_sex': user_sex,
            'user_address': user_address,
            'user_weizhi': '0',
            'user_renzheng': user_renzheng,
            'user_oneword': user_oneword,
            'user_wbnum': user_wbnum,
            'user_follow': user_follow,
            'user_fan': user_fan,
            'user_url': url_user,
            'keyword': keyword
            }
    userinfo.append(user)
    return userinfo


'''获取所有涉及关键字的微博用户，并进行每个用户的基本信息爬取'''


def search_all_user(keyword):
    cookie = Cookie_Process.read_cookie()  # 获取文件中存储的cookie

    mhf = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
    sqlf = "select wb_userid from keyword_weibo where keyword = %s "
    all_id_temp = mhf.findAll(sqlf, keyword)  # 查询涉及到关键字的所有的用户ID
    all_id = []  # 对要爬取的用户id列表进行去重
    for i in all_id_temp:
        if i not in all_id:
            all_id.append(i)
    id_num = len(all_id)
    print('查询到涉及关键字为 {} 的微博用户总数量为 {}\n'.format(keyword, str(id_num)))

    mh = mysqlHelper(get_db()[0], get_db()[1], get_db()[2], get_db()[3], get_db()[4], int(get_db()[5]))
    sql = "insert into keyword_userinfo(user_id,user_name,user_sex,user_address,user_weizhi,user_renzheng,user_oneword,user_wbnum,user_follow,user_fan,user_url,keyword) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    userinfos = []
    for i in range(len(all_id)):
        temp_user_data = fetch_user_data(int(all_id[i][0]), keyword, cookie)

        if (temp_user_data != None):  # 判断返回的用户数据列表是否为空
            userinfos.extend(temp_user_data)

        if ((i + 1) % 50 == 0):  # 每多少条数据执行一次 提交 插入数据库操作
            mh.open();
            for i in range(len(userinfos)):
                mh.cud(sql, (userinfos[i]['user_id'], userinfos[i]['user_name'], userinfos[i]['user_sex'],
                             userinfos[i]['user_address'], userinfos[i]['user_weizhi'], userinfos[i]['user_renzheng'],
                             userinfos[i]['user_oneword'], userinfos[i]['user_wbnum'],
                             userinfos[i]['user_follow'], userinfos[i]['user_fan'], userinfos[i]['user_url'], keyword))
            mh.tijiao();
            mh.close()
            userinfos = []  # 提交数据库之后将列表清空

    if len(userinfos) > 0:  # 将余下的数据提交数据库
        mh.open();
        for i in range(len(userinfos)):
            mh.cud(sql, (userinfos[i]['user_id'], userinfos[i]['user_name'], userinfos[i]['user_sex'],
                         userinfos[i]['user_address'], userinfos[i]['user_weizhi'], userinfos[i]['user_renzheng'],
                         userinfos[i]['user_oneword'], userinfos[i]['user_wbnum'],
                         userinfos[i]['user_follow'], userinfos[i]['user_fan'], userinfos[i]['user_url'], keyword))
        mh.tijiao();
        mh.close()


if __name__ == '__main__':
    Cookie_Process.write_cookie()

    time_start = time.time()
    search_all_user(input('请输入关键字:'))
    time_end = time.time()

    print('本次操作数据全部爬取成功，爬取用时秒数:', (time_end - time_start))
