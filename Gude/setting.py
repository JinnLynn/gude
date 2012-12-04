﻿# -*- coding: utf-8 -*-
import os

# 是否开发模式
DEV_MODE = True

# 版本
VERSION = '0.2'

# 自我介绍
SELF_INTRODUCTION = 'Gude v%s' % VERSION

# 默认测试服务器端口
DEFAULT_SERVER_PORT = 8910

# 脚本目录
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

# 站点目录
SITE_PATH = os.path.abspath(os.curdir)

DEFAULT_CONFIG_FILE = 'site.yaml'
DEFAULT_CONFIG = {
    'domain':               'http://localhost/',
    'root':                 '/',
    'articles_per_page':    5,
    'categories':           [],

    'default_layout':       'post',
}

# 站点下包含的目录     文章       发布       静态文件   本地主题
SITE_INCLUDE_DIR = ['content', 'deploy', 'static', 'theme']

SITE_CONFIG_TEMPLATE= u"""---
domain:                 'http://YOURDOMAIN.com/'
subdirectory:           '/'
theme:                  'default'
title:                  'YOUR SITE TITLE'
tagline:                'YOUR SITE TAGLINE'
author:                 'YOUR NAME'
category:               ['Misc']

num_per_page:           5
num_in_feed:            10
num_in_archive:         50

disgus_shortname:       'YOUR DISGUS SHORTNAME'

default_layout:         'post'

# 指定生成的文件名 KEY: 相对文章目录 VALUE: 相对发布目录
#designated:
#    '1999-08-25-projects.md':   'projects/index.html'

content_filter:         ['Shortcode', 'CenterElement']

# 拷贝文件 KEY: 相对站点工作目录 VALUE: 相对发布目录
#file_copy:
#    'static/htaccess':         '.htaccess'
#    'static/CNAME':             'CNAME'

# publish: git gitftp
publish_type:           'YOUR PUBLISH TYPE'

# 如果是github_project_page 则deploy发布到gh-pages分支 site内容发布
# 否则deploy发布到master 站点原始发布到source
github_project_page:    no
git_remote:             'YOUR GITHUB REPO URL'

# 为避免在使用GIT时提交本配置文件时泄露FTP信息，FTP服务器的配置在 ftp-config.yaml
# 其键值为ftp_server、 ftp_usr、 ftp_pwd

# 开发模式
dev_domain:             'http://localhost:8910'
dev_subdirectory:       '/'
...
"""

DEFAULT_FTP_CONFIG_FILE = 'ftp-config.yaml'
SITE_FTP_CONFIG_TEMPLATE = u"""---
ftp_server:             'YOUR FTP SERVER'
ftp_usr:                'YOUR FTP USER'
ftp_pwd:                'YOUR FTP PASSWORD'
...
"""

# 文章相关配置
# 生成模板
ARTICLE_TEMPLATE = """---
title:      %s
date:       %s
layout:     %s
category:   []
tag:        []
---
"""

# 支持的文章文件名后缀 
ARTICLE_EXTENSION =['md', 'markdown', 'html']

# 忽略的文章目录         标签    所有标签  分类        存档        文章 默认位置   资源       首页分页
ARTICLE_EXCLUDE_DIR = ['tag', 'tags',  'category', 'archive', 'article',    'assets', 'page' ]

# 文章日期支持格式       2001-03-25 13:09:10  2001-03-25 13:10  2001-03-25   03/25/01 13:09:10 03/25/01 13:09:10
ARTICLE_DATE_FORMAT =['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d',  '%c',              '%x'           ]

ARTICLE_FILENAME_PREFIX_FORMAT = '%Y-%m-%d-'
ARTICLE_FILENAME_PREFIX_LEN = 11 # 形如 2001-01-02-FILENAME

# 生成网站时不删除的文件 在deploy
DEPLOY_UNDELETE_FILES = ['.git', '.gitignore', 'README.md']

# GIT 忽略文件列表
GITIGNORE_SITE = u"""
/deploy/
ftp-config.yaml

*.pyc

# Windows
[Dd]esktop.ini
[Tt]humbs.db
$RECYCLE.BIN/

# MacOSX
.DS_Store
._*
.Spotlight-V100
.Trashes
"""

GITIGNORE_DEPLOY = u"""
# Windows
[Dd]esktop.ini
[Tt]humbs.db
$RECYCLE.BIN/

# MacOSX
.DS_Store
._*
.Spotlight-V100
.Trashes
"""

README_TEMPLATE = """
# A personal website powered by [Gude][]. 

## What is Gude?

[Gude][] is a simple static site generator, written in Python.

* Simple, very easy to use
* Work with GIT & GitHub
* Completely static output

[Gude]: http://jeeker.net/projects/gude/
"""