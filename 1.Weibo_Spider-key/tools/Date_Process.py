# -*- coding:utf-8 -*-
import datetime

''' 微博创建日期处理函数 '''


def time_process(time):
    time = str(time)
    if '月' in time:
        if '年' not in time:
            dangqian_year = datetime.datetime.now().strftime('%Y')
            time = dangqian_year + '-' + time
        time = time.replace(r'年', '-').replace(r'月', '-').replace(r'日', '')
    if time.startswith('今天'):
        dangqian_date = datetime.datetime.now().strftime('%Y-%m-%d')
        time = time.replace(r'今天', dangqian_date + ' ')
    if time.endswith('分钟前'):
        dangqian_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        time = dangqian_time
    return time
