# -*- coding:utf-8 -*-

''' 转发、评论数处理函数 '''


def num_process(char_num):
    if (len(char_num) <= 3):
        return '0'
    else:
        return str(char_num.split()[1])
