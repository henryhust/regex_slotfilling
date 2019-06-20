# -*- coding:utf-8 -*-

'''获取文件中存储的cookie'''


def read_cookie():
    with open('cookie_file', 'r', encoding='utf-8') as f:  # 打开文件
        line = f.readline()  # 读取所有行
    f.close()
    return line


'''更新文件中存储的cookie'''


def write_cookie():
    temp = input("请更新在谷歌浏览器登录weibo.cn时所获取的cookie（输入n/N不更新cookie）:")
    if (temp == 'n' or temp == 'N'):
        return
    cookie = temp
    with open('cookie_file', 'w', encoding='utf-8') as f:  # 打开文件
        f.write(cookie)
    f.close()
    return cookie
