#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'

from sys import argv
from os import makedirs, unlink, sep
from os.path import dirname, exists, isdir, splitext
from string import replace, find, lower
from htmllib import HTMLParser
from urllib import urlretrieve
from urlparse import urlparse, urljoin
from formatter import DumbWriter, AbstractFormatter
from cStringIO import StringIO

class Retriever(object):#download web page
    def __init__(self, url):
        self.url = url
        self.file = self.filename(url)

    #local filename ,directory
    def filename(self, url, deffile = "index.htm"):
        parseurl = urlparse(url, 'http:', 0)
        path = parseurl[1] + parseurl[2]

        #将路径转换为一个元组，如果为目录则第二个元素为空，如果文件则第二个元素为文件扩展名
        #path = "D:/pycharmProjects/PythonWebApp/weblearning/Crawl.py"
        #print splitext(path)
        #('D:/pycharmProjects/PythonWebApp/weblearning/Crawl', '.py')

        ext = splitext(path)
        if ext[1] == '':#no file use default
            #tuple[-index],倒数第index个元素
            if path[-1] == '/':
                path += deffile
            else:
                path += '/' + deffile
        #获取path的dir,
        # path=D:/pycharmProjects/PythonWebApp/webLearning
        # dir(path)=D:/pycharmProjects/PythonWebApp
        ldir = dirname(path)#local directory
        if sep != '/': #os-indep. path separator
            ldir = replace(ldir, '/', sep)
        if not isdir(ldir): #create archive dir if nec.
            #如果存在文件，则删除
            if exists(ldir):
                unlink(ldir)
            makedirs(ldir)
        return path

    def download(self):
        #urlretrieve()返回一个2元组，（filename,mime_hdrs）
        try:
            retval = urlretrieve(self.url, self.file)
        except IOError:
            retval = ('*** ERROR: invalid URL "%s"' %self.url,)
            print 'erro,invalid url'
        return retval

    def parseAndGetLinks(self):#parse HTML , save links
        self.parser = HTMLParser(AbstractFormatter(DumbWriter(StringIO())))
        self.parser.feed(open(self.file).read())
        self.parser.close()
        return self.parser.anchorlist

class Crawler(object): #manage entire crawling process
    count = 0 #static downloaded page counter
    def __init__(self, url):
        self.q = [url]
        self.seen = []
        self.dom = urlparse(url)[1]

    def getPage(self, url):
        r = Retriever(url)
        retval = r.download()
        print 'hehe', retval
        if retval[0] == '*':#erro situation, do not parse
            print retval, ',,, skippig parse'
            return
        Crawler.count += 1
        print '\n(', Crawler.count, ')'
        print 'URL:', url
        print 'FILE:', retval[0]
        self.seen.append(url)

        links = r.parseAndGetLinks()#get and process links
        for eachLink in links:
            if eachLink[:4] != 'http' and \
                find (eachLink, '://') == -1:
                eachLink = urljoin(url, eachLink)
            print '* ', eachLink,

            if find(lower(eachLink), 'mailto:') != -1:
                print '... discarded, mailto link'
                continue

            if eachLink not in self.seen:
                if find(eachLink, self.dom) == -1:
                    print '... doscarder, not in domain'
                else:
                    if eachLink not in self.q:
                        self.q.append(eachLink)
                        print '...new, added to q'
                    else:
                        print '...discarded, already in q'
            else:
                print '...discarded, already processed'


    def go(self):#process links in q
        while self.q:
            url = self.q.pop()
            self.getPage(url)

def main():
        if len(argv) > 1:
            url = argv[1]
        else:
            try:
                url = raw_input("Enter starting URL: ")
            except(KeyboardInterrupt, EOFError):
                url = ''
            if not url:
                return
        robot = Crawler(url)
        robot.go()

if __name__ == '__main__':
    main()



















