#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'

#字符统计，统计文本中除空格以外的字符数目
with open("hh.txt", 'r') as f:
    res = 0
    res1 = 0
    for line in f:
        res1 +=1
        for word in line.split():
            res +=len(word)
print res1, res

'文件过滤，显示一个文件的所有行，忽略#开头的行'
with open('hh.txt','r') as f:
    for line in f:
        if line[0] == '#':
            pass
        else:
            print line


N = raw_input('Please input the paramter N:')
print 1








