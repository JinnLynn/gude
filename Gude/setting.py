# -*- coding: utf-8 -*-
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
DEFAULT_PRIVACY_CONFIG_FILE = 'privacy.yaml'
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
domain:                 HTTP://YOURDOMAIN.COM/
subdirectory:           /
title:                  YOUR SITE TITLE
tagline:                YOUR SITE TAGLINE
author:                 YOUR NAME
category:               [Other]

num_per_page:           5
num_in_feed:            10
num_in_archive:         50

theme:                  default
default_layout:         post

# 头部菜单 默认已包括首页 Home
header_menu:
    - title:            Tags
      url:              HTTP://YOURDOMAIN.COM/tags/
    - title:            Archives
      url:              HTTP://YOURDOMAIN.COM/archives/

# 外部服务设置
disgus_shortname:           YOUR DISGUS SHORTNAME
google_analytics_track_id:  YOUR GOOGLE ANALYTICS TRACK ID
# 如果使用了第三方Feed托管服务，则将其产生的Feed地址配置于此，留空将使用本地默认
feed_url:                   ~

# 指定生成的文件名 src: 相对content目录 dst: 相对deploy目录
#designated:
#    - src:      2000-01-01-projects.md
#      dst:      projects/index.html

content_filter:         [Shortcode, CenterElement]

# 拷贝文件 src: 相对站点static目录 dst: 相对deploy目录
# 支持通配符
#file_copy:
#    - src:      favicon.ico
#      dst:      assets/images/favicon.ico
#    - src:      uploads/*
#      dst:      assets/uploads/

# 本地模式
local_domain:           http://localhost:8910
local_subdirectory:     /

# 与服务器相关的配置见privacy.yaml

...
"""

SITE_PRIVACY_CONFIG_TEMPLATE = u"""---
# publish: git gitftp
publish_type:           YOUR PUBLISH TYPE

# 如果是github_project_page 则deploy发布到gh-pages分支 site内容发布
# 否则deploy发布到master 站点原始发布到source
github_project_page:    no

git_remote:             YOUR GITHUB REPO URL

ftp_server:             YOUR FTP SERVER
ftp_subdirectory:       YOUR FTP SERVER SUBDIRECTORY
ftp_usr:                YOUR FTP USER
ftp_pwd:                YOUR FTP PASSWORD
...
"""

# 文章相关配置
# 生成模板
ARTICLE_TEMPLATE = """<!--
title:      %s
date:       %s
category:   ~
tag:        ~%s
-->

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
privacy.yaml

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
# 网站统计跟踪代码模板
SITE_TRACK_TEMPLATE = """
<!-- google analytics track code -->
<script type="text/javascript">
    var _gaq = _gaq || [];
    _gaq.push(['_setAccount', '%s']);
    _gaq.push(['_trackPageview']);

    (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
    })();
</script>
"""

# disgus 评论
DISGUS_COMMENT_TEMPLATE = """
<!-- DISGUS Comment BEGIN -->
    <div id="disqus_thread"></div>
    <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments.</a></noscript>
    <a href="http://disqus.com" class="dsq-brlink">comments powered by <span class="logo-disqus">Disqus</span></a>
    <script type="text/javascript">
        var disqus_shortname = '{shortname}';
        (function() {{
            var dsq = document.createElement('script'); 
            dsq.type = 'text/javascript'; 
            dsq.async = true;
            dsq.src = 'http://'+ disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        }}());
    </script>
<!-- DISGUS Comment END -->
"""

# 多说评论
DUOSHUO_COMMENT_TEMPLATE = """
<!-- Duoshuo Comment BEGIN -->
    <div class="ds-thread" data-title="{page-title}"></div>
    <script type="text/javascript">
        var duoshuoQuery = {{short_name:"{shortname}"}};
        (function() {{
            var ds = document.createElement('script');
            ds.type = 'text/javascript';
            ds.async = true;
            ds.src = 'http://static.duoshuo.com/embed.js';
            ds.charset = 'UTF-8';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(ds);
        }})();
    </script>
<!-- Duoshuo Comment END -->
"""

COMMENT_TEMPLATE = { 'duoshuo'   : DUOSHUO_COMMENT_TEMPLATE,
                     'disqus'    : DISGUS_COMMENT_TEMPLATE
                   }