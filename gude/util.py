﻿# -*- coding: utf-8 -*-
import sys, os, re, urllib, codecs, logging, shutil
from datetime import datetime
import time

import markdown2

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

markdown = lambda s: markdown2.markdown(s, extras=['footnotes', 'toc', 'fenced-code-blocks', 'cuddled-lists', 'wiki-tables'])

# 根据本地时区转换成UTC时间 
toUTC = lambda d: d - (datetime.now() - datetime.utcnow()) if isinstance(d, datetime) else datetime.utcnow()
# 以ISO 8601输出UTC时间
toUTCISO8601 = lambda d = None: toUTC(d).strftime('%Y-%m-%dT%H:%M:%SZ')

# 时间戳
timestamp = lambda d = None: int( time.time() if not isinstance(d, datetime) else time.mktime(d.timetuple()) )

# 文件hash
fileHash = lambda f: '{}'.format( '' if not os.path.isfile(f) else int (os.stat(f).st_mtime) )

# 文件创建时间
fileCreateDate = lambda f: datetime.now() if not os.path.isfile(f) else datetime.fromtimestamp( int( os.stat(f).st_ctime ) )

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

def tryToList(var):
    if isinstance(var, (str, unicode)):
        return map(lambda s:s.strip(), var.split(','))
    return [] if not isinstance(var, list) else var

# 编码为网址资源组件
def urlQuote(s):
    try:
        return urllib.quote( re.sub('[- ]+', '-', s.lower() ))
    except Exception, e:
        return urllib.quote( re.sub('[- ]+', '-', s.lower() ).encode('utf-8'))

def die(msg=''):
    if len(msg):
        sys.stderr.write(msg + '\n')
    sys.exit(1)

def getRelativePath(abspath):
    assert abspath.find(SITE_PATH) == 0, 'path error. %s' % abspath
    return abspath[len(SITE_PATH)+1:]

# 拷贝文件树 shutil.copytree当拷贝的目标文件夹内已经包含了需拷贝的文件夹时会出错
def copytree(src, dst):
    names = os.listdir(src)
    if not os.path.isdir(dst):
        os.makedirs(dst)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname)
            else:
                shutil.copy2(srcname, dstname)
        except Exception, e:
            print(e)
    try:
        shutil.copystat(src, dst)
    except Exception, e:
        print(e)

# 命令是否存在
def isCommandExists(program):
    is_exe = lambda f: os.path.isfile(f) and os.access(f, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True
    return False

# 日志处理
def logInit():
    logger = logging.getLogger()
    #filehandler = logging.FileHandler('log.log')
    streamhandler = logging.StreamHandler()
    #fmt = logging.Formatter('%(asctime)s, %(funcName)s, %(message)s')
    logger.setLevel(logging.WARNING)
    #logger.addHandler(filehandler)
    logger.addHandler(streamhandler)
    return logger

LOGGER = logInit()

def logLevelSet(level):
    LOGGER.setLevel(level)

def logError(msg, *args, **kwargs):
    LOGGER.error(msg, *args, **kwargs)

def logWarning(msg, *args, **kwargs):
    LOGGER.warning(msg, *args, **kwargs)

def logInfo(msg, *args, **kwargs):
    LOGGER.info(msg, *args, **kwargs)

def logDebug(msg, *args, **kwargs):
    LOGGER.debug(msg, *args, **kwargs)

def logAlways(msg, *args, **kwargs):
    LOGGER.critical(msg, *args, **kwargs)