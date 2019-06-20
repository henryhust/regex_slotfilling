# -*- coding:utf-8 -*-
import datetime
import re

'''对要搜索的时间期限进行以每小时为单位的划分功能模块'''


def hour_slice(start__time, end_time):
    chai_start = start__time.split('.');  # 将起始时间节点字符串进行分割
    chai_end = end_time.split('.')

    chai_start_year = int(chai_start[0])  # 获取起始时间的年、月、日、时
    chai_start_month = int(chai_start[1])
    chai_start_day = int(chai_start[2])
    try:
        chai_start_hour = int(chai_start[3])
    except:
        chai_start_hour = int(0)

    chai_end_year = int(chai_end[0])
    chai_end_month = int(chai_end[1])
    chai_end_day = int(chai_end[2])
    try:
        chai_end_hour = int(chai_end[3])
    except:
        chai_end_hour = int(0)

    begin = datetime.date(chai_start_year, chai_start_month, chai_start_day)
    end = datetime.date(chai_end_year, chai_end_month, chai_end_day)
    cha_day = re.split('[:]', str(end - begin))[0]
    cha_day = cha_day.strip().split(" ")[0]
    print('搜索时间间隔天数为：' + cha_day + '天')  # 计算起始时间相隔几天

    hour_liebiao = []

    if (chai_start_month < 10):  # 对拆分的起始时间的年、月、日、时进行小于10时加'0'的格式化操作
        chai_start_month_0 = '0' + str(chai_start_month)
    else:
        chai_start_month_0 = str(chai_start_month)

    if (chai_start_day < 10):
        chai_start_day_0 = '0' + str(chai_start_day)
    else:
        chai_start_day_0 = str(chai_start_day)

    if (chai_end_month < 10):
        chai_end_month_0 = '0' + str(chai_end_month)
    else:
        chai_end_month_0 = str(chai_end_month)

    if (chai_end_day < 10):
        chai_end_day_0 = '0' + str(chai_end_day)
    else:
        chai_end_day_0 = str(chai_end_day)

    if (cha_day == '0'):  # 搜索日期为同一天的情况
        new_hour = chai_start_hour
        for i in range(chai_end_hour - chai_start_hour):
            start__time_hour = str(chai_start_year) + '-' + chai_start_month_0 + '-' + chai_start_day_0 + '-' + str(
                new_hour)
            end_time_hour = str(chai_start_year) + '-' + chai_start_month_0 + '-' + chai_start_day_0 + '-' + str(
                chai_start_hour + i + 1)
            hour_liebiao.append([start__time_hour, end_time_hour])
            new_hour = chai_start_hour + i + 1

    if (cha_day == '1'):  # 搜索日期相差一天的情况
        new_hour = chai_start_hour
        for i in range(24 - chai_start_hour):
            start__time_hour = str(chai_start_year) + '-' + chai_start_month_0 + '-' + chai_start_day_0 + '-' + str(
                new_hour)
            end_time_hour = str(chai_start_year) + '-' + chai_start_month_0 + '-' + chai_start_day_0 + '-' + str(
                chai_start_hour + i + 1)
            hour_liebiao.append([start__time_hour, end_time_hour])
            new_hour = chai_start_hour + i + 1

        new_start_hour = 0
        new_end_hour = 0
        for i in range(chai_end_hour):
            start__time_hour = str(chai_end_year) + '-' + chai_end_month_0 + '-' + chai_end_day_0 + '-' + str(
                new_start_hour)
            end_time_hour = str(chai_end_year) + '-' + chai_end_month_0 + '-' + chai_end_day_0 + '-' + str(
                new_end_hour + i + 1)
            hour_liebiao.append([start__time_hour, end_time_hour])
            new_start_hour = new_end_hour + i + 1

    if (int(cha_day) > 1):  # 搜索日期相差大于一天的情况
        new_hour = chai_start_hour
        for i in range(24 - chai_start_hour):
            start__time_hour = str(chai_start_year) + '-' + chai_start_month_0 + '-' + chai_start_day_0 + '-' + str(
                new_hour)
            end_time_hour = str(chai_start_year) + '-' + chai_start_month_0 + '-' + chai_start_day_0 + '-' + str(
                chai_start_hour + i + 1)
            hour_liebiao.append([start__time_hour, end_time_hour])
            new_hour = chai_start_hour + i + 1

        new_begin = datetime.date(chai_start_year, chai_start_month, chai_start_day)
        new_end = datetime.date(chai_end_year, chai_end_month, chai_end_day)
        for j in range((new_end - new_begin).days + 1):
            day = new_begin + datetime.timedelta(days=j)
            for k in range(24):
                start__time_hour = str(day) + '-' + str(k)
                end_time_hour = str(day) + '-' + str(k + 1)
                if (str(day) == (str(chai_start_year) + '-' + str(chai_start_month) + '-' + str(
                        chai_start_day)) and k < chai_start_hour + 1):
                    continue
                else:
                    hour_liebiao.append([start__time_hour, end_time_hour])

        new_start_hour = 0
        new_end_hour = 0
        for i in range(chai_end_hour):
            start__time_hour = str(chai_end_year) + '-' + chai_end_month_0 + '-' + chai_end_day_0 + '-' + str(
                new_start_hour)
            end_time_hour = str(chai_end_year) + '-' + chai_end_month_0 + '-' + chai_end_day_0 + '-' + str(
                new_end_hour + i + 1)
            hour_liebiao.append([start__time_hour, end_time_hour])
            new_start_hour = new_end_hour + i + 1

    new_hour_liebiao = []  # 对分隔列表中的时间进行去重
    for i in hour_liebiao:
        if i not in new_hour_liebiao:
            new_hour_liebiao.append(i)

    print('时间分隔列表如下：' + str(new_hour_liebiao))
    print('爬取单位小时总数：' + str(len(new_hour_liebiao)))
    print('\n')
    return new_hour_liebiao
