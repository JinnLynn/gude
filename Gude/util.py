# -*- coding: utf-8 -*-
import sys, os, re, urllib
import setting
from setting import DEV_MODE
from setting import SITE_PATH

# 标准化字典键名
stdKey = lambda s: re.sub('[- ]+', '_', s.lower())
# 模板
tplFile = lambda s: '%s.mako' % s
# 创建slug 使用urlQuote
generateSlug = lambda s: urlQuote(s)


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

def subcommand():
    if not sys.argv[1:]:
        return
    return sys.argv[1]

def isOptExists(opt):
    if not isinstance(opt, str):
        return False
    args = sys.argv[2:]
    for arg in args:
        arg = arg.lower()
        if not arg.startswith('-'):
            continue
        if arg.find(opt):
            return True
    return False

def getRelativePath(abspath):
    assert abspath.find(SITE_PATH) == 0, 'path error. %s' % abspath
    return abspath[len(SITE_PATH)+1:]

def self():
    return 'Gude %s' % setting.VERSION
    pass