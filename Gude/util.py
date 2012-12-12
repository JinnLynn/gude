# -*- coding: utf-8 -*-
import sys, os, re, urllib, codecs
from datetime import datetime
import time

from markdown import markdown as MarkdownConvert

from setting import *

# 标准化字典键名
stdKey = lambda s: re.sub('[- ]+', '_', s.lower())
# 模板
tplFile = lambda s: '%s.mako' % s
# 创建slug 使用urlQuote
generateSlug = lambda s: urlQuote(s)
# 清理/ 多于一个的/将整理为一个
cleanSlash = lambda s: re.sub('//+', '/', s)
# 标准化路径： 联系多个'-'转为一个 空格转为 '-'
standardizePath = lambda s: cleanSlash( re.sub('[- ]+', '-', s.lower()) )

markdown = lambda s: MarkdownConvert(s, ['fenced_code']) 

# UTC时间字符串
utcNow = lambda: '%s UTC' % datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

# 时间戳
timestamp = lambda d = None: int( time.time() if not isinstance(d, datetime) else time.mktime(d.timetuple()) )

# 文件hash
fileHash = lambda f: '%d' % ( 0 if not os.path.isfile(f) else int (os.stat(f).st_mtime) )

# 文件修改时间
fileModifyDate = lambda f: datetime.now() if not os.path.isfile(f) else datetime.fromtimestamp( int( os.stat(f).st_mtime ) )

parseTemplateString = lambda t, r: (t % r).strip('\n\r\t')

# 文件写入
#writeToFile = lambda f, c: with codecs.open(f, 'w', encoding='utf-8') as fp: ( fp.write(c) )
def writeToFile(f, c):
     with codecs.open(f, 'w', encoding='utf-8') as fp:
        fp.write(c)


# 如果文件夹不存在则创建
def tryMakeDir(dirpath):
    if not os.path.isdir( dirpath ):
        os.makedirs( dirpath ) 
# 如果文件所在的文件夹不存在则创建
def tryMakeDirForFile(filepath):
    if not os.path.isdir( os.path.dirname( filepath ) ):
        os.makedirs(os.path.dirname( filepath )) 
                

# 编码为网址资源组件
def urlQuote(s):
    try:
        return urllib.quote( re.sub('[- ]+', '-', s.lower() ))
    except Exception, e:
        return urllib.quote( re.sub('[- ]+', '-', s.lower() ).encode('utf-8'))

def die(msg):
    sys.stderr.write(msg + '\n')
    sys.exit(1)

def log(msg):
    if DEV_MODE:
        print 'LOG:', msg

def getRelativePath(abspath):
    assert abspath.find(SITE_PATH) == 0, 'path error. %s' % abspath
    return abspath[len(SITE_PATH)+1:]