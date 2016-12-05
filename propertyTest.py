#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import functools
class Student(object):
    #property的本质是个装饰器
    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not isinstance(value, int):
            raise ValueError('score must be an integer!')
        if value < 0 or value > 100:
            raise ValueError('score must between 0 ~ 100!')
        self._score = value


#装饰器模式：调用log,返回的是wrapper的地址，接着调用wrapper,
# 返回的是func的地址，调用func
def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        #print "hi"
        print "execute %s"%(func.__name__)
        #print "hi"
        func(*args, **kwargs)
        print "hi"
    return wrapper

def log1(text=None):
    def decrote(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
             print text
             print "execute %s"%(func.__name__)
             #if not text == None:
              #   print text
             return func(*args, **kwargs)
        return wrapper
    return decrote




@log
@log1("run")
def add(a, b):
    print a+b
    return a+b

#test
s = Student()
s.score = 60
print('s.score =', s.score)
# ValueError: score must between 0 ~ 100!
#s.score = 9999
add(1, 2)
print add.__name__

