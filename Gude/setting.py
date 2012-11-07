# -*- coding: utf-8 -*-
import os

# 是否开发模式
DEV_MODE = True

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
    'extension':            'html'
}

# 文章相关配置
# 生成模板
ARTICLE_TEMPLATE = """---
layout:     post
title:      Untitled
date:       %s
category:   []
tag:        []
---
"""

# 支持的文章文件名后缀 
ARTICLE_EXTENSION =['md', 'markdown' 'html']

# 忽略的文章目录
ARTICLE_EXCLUDE_DIR = ['tag', 'category']

HELP_DOC = """
    init [-f]
    add FILENAME
    build [-c]
    serve [PORT] 
"""