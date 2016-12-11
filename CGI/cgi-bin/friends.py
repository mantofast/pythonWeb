#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import cgi
reshtml = '''Content-Type: text/html\n
<html><head><title>
Friends CGI demo (dynamic screen)
</title></head>
<body><h3>Friends list for :<I>%s</I></h3>
Your name is <B>%s</B><P>
Your have <B>%s</B> friends.
</body></html>'''

form = cgi.FieldStorage()
who = form['person'].value
howmany = form['howmany'].value
print reshtml % (who, who, howmany)
