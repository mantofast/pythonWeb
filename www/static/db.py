#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'

#db.py :实现数据库模块
"""
设计db模块的原因：
  1. 更简单的操作数据库
      一次数据访问：   数据库连接 => 游标对象 => 执行SQL => 处理异常 => 清理资源。
      db模块对这些过程进行封装，使得用户仅需关注SQL执行。
  2. 数据安全
      用户请求以多线程处理时，为了避免多线程下的数据共享引起的数据混乱，
      需要将数据连接以ThreadLocal对象传入。
设计db接口：
  1.设计原则：
      根据上层调用者设计简单易用的API接口
  2. 调用接口
      1. 初始化数据库连接信息
          create_engine封装了如下功能:
              1. 为数据库连接 准备需要的配置信息
              2. 创建数据库连接(由生成的全局对象engine的 connect方法提供)
          from transwarp import db
          db.create_engine(user='root',
                           password='password',
                           database='test',
                           host='127.0.0.1',
                           port=3306)
      2. 执行SQL DML
          select 函数封装了如下功能:
              1.支持一个数据库连接里执行多个SQL语句
              2.支持链接的自动获取和释放
          使用样例:
              users = db.select('select * from user')
              # users =>
              # [
              #     { "id": 1, "name": "Michael"},
              #     { "id": 2, "name": "Bob"},
              #     { "id": 3, "name": "Adam"}
              # ]
      3. 支持事务
         transaction 函数封装了如下功能:
             1. 事务也可以嵌套，内层事务会自动合并到外层事务中，这种事务模型足够满足99%的需求
"""

import MySQLdb
import threading
import functools
import logging


#全局变量
engine = None

def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    #import mysql.connector
    global engine
    if engine is not None:
        raise DBError('Engine is already initialized.')
    params = dict(user=user, password=password, database=database, host=host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False)
    for k, v in defaults.iteritems():
        params[k] = kw.pop(k, v)
    params.update(kw)
    params['buffered'] = True
    #engine = _Engine(lambda: mysql.connector.connect(**params))
    engine = _Engine(lambda: MySQLdb.connect(**params))
    # test connection...
    logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))



#数据库引擎对象
#单下划线常用于module中，表示内部变量和内部函数，在其他模块import的时候是不可见的
class _Engine(object):
    #构造函数，获取数据库链接
    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect


#数据库上下文对象，继承threading.local类，原理--全局变量，key为thread_id
class _DbCtx(threading.local):
    #构造函数：初始时数据库链接为空，事务计数为0
    def __init__(self):
        self.connection = None
        self.transcations = 0

    #判断链接是否初始化过
    def is_init(self):
        return not self.connection is None

    #初始化数据库链接，获取惰性数据库链接，即还未使用到游标的链接
    def init(self):
        self.connection = _LasyConnection()
        self.transcations = 0

    #清空数据库连接
    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    #获取游标
    def cursor(self):
        return self.connection.cursor()

#定义全局变量，threadlocal变量，数据库上下文对象
_db_ctx = _DbCtx()


#数据库连接上下文类，即每个数据库链接创建的上下文,处理资源的释放
#必须有enter和exit方法
class _ConnectionCtx(object):
    #__enter__函数：进入一个链接的上下文空间，global引入所要操作的全局变量
    #with语句执行前会调用enter方法
    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self
    #with语句执行后会调用exit方法
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()

class _LasyConnection(object):

    def __init__(self):
        #其实并未创建真正的连接，这只是一个幌子
        self.connection = None

    def cursor(self):
        global engine
        if self.connection is None:
            self.connection = engine
        return engine.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            _connection = self.connection
            self.connection = None
            logging.info('[CONNECTION] [CLOSE] connection <%s>...' % hex(id(connection)))
            _connection.close()

def connection():
    """
    db模块核心函数，用于获取一个数据库连接
    通过_ConnectionCtx对 _db_ctx封装，使得惰性连接可以自动获取和释放，
    也就是可以使用 with语法来处理数据库连接
    _ConnectionCtx    实现with语法
    ^
    |
    _db_ctx           _DbCtx实例
    ^
    |
    _DbCtx            获取和释放惰性连接
    ^
    |
    _LasyConnection   实现惰性连接
    """
    return _ConnectionCtx()


#装饰器模式，用装饰器封装with语句，使得用户更关注于被装饰的对象，即用户自己想要实现的功能
def with_connection(func):
    """
       设计一个装饰器 替换with语法，让代码更优雅
       比如:
           @with_connection
           def foo(*args, **kw):
               f1()
               f2()
               f3()
       """

    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)

    return _wrapper

@with_connection
def _select(sql, first, *args):
    """
    执行SQL，返回一个结果 或者多个结果组成的列表
    """
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    logging.info('SQL: %s, ARGS: %s' % (sql, args))
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if first:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names, values)
        return [Dict(names, x) for x in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()



@with_connection
def update(sql, *args):
    pass

#事务的上下文对象
class _TransactionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_close_connection = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_conn = True

    #事务计数
        _db_ctx.transactions = _db_ctx.transactions + 1
        return self


    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

def with_transaction(func):
    @functools.wraps(func)
    def wrappers(*args, **kwargs):
        with _TransactionCtx():
            return func(*args, **kwargs)
    return wrappers

@with_transaction
def















