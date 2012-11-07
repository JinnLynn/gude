# -*- coding: utf-8 -*-
import sys, os, codecs, random
from datetime import datetime

import yaml
from markdown import markdown
from mako.lookup import TemplateLookup

import util
from setting import SITE_PATH

"""
文章信息

layout   : 布局名称
title    : 标题
date     : 发布时间
tags     : 标签
category : 分类

source   : 原始文件名
content  : 内容
dirname  : 相对目录名称
basename : 文件名称 无后缀
extension : 后缀
"""
DEFAULT_ARTICLE_CONFIG = {
    'layout': 'post',
    'title' : 'untitied'
}

""" 单篇文章 """
class Article(object):
    
    def __init__(self, site, source):
        self.site = site
        self.source = source

        self.layout = 'post'
        self.title = 'untitled'
        self.date = None
        self.author = self.site.author
        self.tags = []
        self.category = []

        self.content = ''
        self.summary = ''

        self.metadata = {}

        self.unique = ''.join(random.sample('9876543210zyxwvutsrqponmlkjihgfedcba', 5))

    def parse(self):
        if not os.path.exists(self.source):
            util.log('file non-existent. [%s]' % self.source)
            return False

        fp = codecs.open(self.source, 'r', encoding='utf-8')
        lines = fp.readlines()

        # 解析文章信息
        config_str = ''
        config = {}
        config.update(DEFAULT_ARTICLE_CONFIG)
        index = 1
        for line in lines[1:]:
            index += 1
            if line.find('---') == 0:
                break
            config_str += line
        config.update( yaml.load(config_str) )
        
        self.layout     = config.get('layout', 'post')
        self.title      = config.get('title', 'untitled')
        self.author     = config.get('author', self.site.author)
        self.date       = config.get('date', None)
        self.tag        = config.get('tag', [])
        self.category   = config.get('category', [])
        self.metadata   = config.get('metadata', {})

        # 检查date
        if not self.isDateAvailable() or not self.isCategoryAvailable():
            return False
        
        # 获取内容
        self.content = ''
        self.summary = ''
        for line in lines[index:]:
            if line.strip(' \t') == '<!--more-->':
                self.summary = self.contert
                line = '<span id="more-%s"></span>' % self.unique
            self.content += line

        # 处理 html 与 markdown 格式
        
        if self.isMarkdown():
            self.content = markdown(self.content)
            self.summary = markdown(self.summary)

        return True

    # 文章日期是否有效
    def isDateAvailable(self):
        if self.date == None: 
            return False
        if not isinstance(self.date, datetime):
            if not isinstance(self.date, str):
                return False;
            else:
                self.date = datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')
        if self.date > datetime.now():
            return False
        return True

    # 文章分类是否有效
    def isCategoryAvailable(self):
        return True

    def export(self):
        export_dir = os.path.dirname(self.exportFilePath)
        if export_dir and not os.path.isdir(export_dir):
            os.makedirs(export_dir)
    
        data = {'site': self.site, 'article': self}

        template = self.site.lookup.get_template(util.tplFile(self.layout))
        html = template.render_unicode(**data).strip()
        with open(self.exportFilePath, 'w') as f:
            f.write(html.encode('utf-8'))
        print "  %s \n      => %s" % ( self.site.getRelativePath(self.source), 
                               self.site.getRelativePath(self.exportFilePath) )

    def isMarkdown(self):
        dirname, basename, extension = self.sourceFilePathSplited;
        return extension.find('md') == 0 or extension.find('markdown') == 0

    # 永久链接  
    @property
    def permalink(self):
        dirname, basename, extension = self.sourceFilePathSplited;
        return self.site.generateUrl(dirname, 'article', basename)

    @property
    def sourceFilePathSplited(self):
        dirname, basename = os.path.split(self.source)
        return ( dirname[len( self.site.articlePath )+1:],
                os.path.splitext(basename)[0],
                os.path.splitext(basename)[1][1:]
            )

    # 导出文件的绝对路径
    @property
    def exportFilePath(self):
        dirname, basename, extension = self.sourceFilePathSplited;
        return self.site.generateDeployFilePath(dirname, 'article', basename)

    def output():
        return 'dsf'
        pass

""" 页面导航信息 """
class PageNav(object):
    def __init__(self, articles, num_per_page, first_page_name, other_page_name = 'page-%d'):
        assert isinstance(articles, list) and len(articles) > 0 and num_per_page > 0
        self.articles = articles
        self.num_per_page = num_per_page
        self.first_page_name = first_page_name
        self.other_page_name = other_page_name

    # 页面数
    def getPageCount(self):
        count = len(self.articles) / self.num_per_page;
        if len(self.articles) % self.num_per_page > 0:
            count += 1
        return count

    # 获取特定页面的数据 [articles, deploy_file_name]
    def getDataByPageNum(self, num):
        assert 0 < num <= self.getPageCount()
        start_index = self.num_per_page * (num-1)
        end_index = start_index + self.num_per_page + 1
        deploy_file_name = self.first_page_name;
        if num > 1:
            deploy_file_name = self.other_page_name % num
        return [self.articles[start_index:end_index], deploy_file_name]

""" 文章集合 """
class ArticleBundle(object):
    def __init__(self, site):
        self.site = site
        self.articles = []

    def addArticle(self, article):
        if not isinstance (article, Article):
            raise ValueError, 'type of article is not Article'
        elif article in self.articles:
            raise ValueError, 'article is already exists'
        self.articles.append(article)

    def export(self):
        self.sortByDateDESC()
        template = self.getTemplate()
        assert template, 'template is non-existent'

        first_page_name, other_page_name = self.exportBasename
        pagenav = PageNav(self.articles, self.site.numPerPage, first_page_name, other_page_name)
        total_page = pagenav.getPageCount()
        for i in range(1, total_page+1):

            articles, deploy_file_name = pagenav.getDataByPageNum(i)
            export_file_path = self.site.generateDeployFilePath(self.exportDir, deploy_file_name)

            # 检查输出目录
            if not os.path.isdir( os.path.dirname(export_file_path) ):
                os.makedirs(os.path.dirname(export_file_path))

            data = {'site': self.site, 'articles': articles, 'pagenav': {'cur_page': i, 'total_page': total_page}}
            html = template.render_unicode(**data).strip()
            with open(export_file_path, 'w') as f:
                f.write(html.encode('utf-8'))

    def testPrint(self):
        for a in self.articles:
            print '   ', util.getRelativePath(a.source)

    # 按日期倒序排序
    def sortByDateDESC(self):
        self.articles = sorted(self.articles, key = lambda a: a.date, reverse = True ) 
        pass

    def getTemplate(self):
        return None

    # 输出文件信息 返回为 [相对发布目录的文件夹路径, 第一页文件名, 其它页文件名（带页数格式化%d）]
    #! 文件名不包括后缀
    def getExportFileInfo(self):
        return ['', '', '']

    @property
    def count(self):
        return len(self.articles)

    # 输出目录 相对deploy
    @property
    def exportDir(self):
        return ''

    # 输出文件名称（不包括后缀） [第一页文件名, 其它页文件名（带页数格式化%d）]
    @property
    def exportBasename(self):
        return ['', '']

""" """
class Home(ArticleBundle):
    def __init__(self, site):
        super(Home, self).__init__(site)

    def exportAllArticles(self):
        self.sortByDateDESC()
        print 'article export:'
        map(lambda a: a.export(), self.articles)

    def testPrint(self):
        pass

    def getTemplate(self):
        return self.site.lookup.get_template(util.tplFile('home'))
        
    def getExportFileInfo(self):
        return ['', 'index', 'page-%d']

    @property
    def permalink(self):
        return self.site.generateUrl(self.exportDir, self.category_slug)

    @property
    def exportDir(self):
        return ''
        
    @property
    def exportBasename(self):
        return ['index', 'page-%d']

""" 分类 """
class Category(ArticleBundle):
    def __init__(self, site, category):
        super(Category, self).__init__(site)
        self.category_name = category
        self.category_slug = util.encodeURIComponent(category)

    def testPrint(self):
        print 'Category: %s %s %d' % (self.category_name, self.category_slug, self.count)
        super(Category, self).testPrint()

    def getTemplate(self):
        return self.site.lookup.get_template(util.tplFile('home'))

    @property
    def permalink(self):
        return self.site.generateUrl(self.exportDir, self.category_slug)

    @property
    def exportDir(self):
        return 'category/%s' % self.category_slug

    @property
    def exportBasename(self):
        return ['index', 'page-%d']


""" 标签 """
class Tag(ArticleBundle):
    def __init__(self, site, tag):
        super(Tag, self).__init__(site)
        self.tag_name = tag
        self.tag_slug = util.encodeURIComponent(tag)

    def testPrint(self):
        print 'Tag: %s %s %d' % (self.tag_name, self.tag_slug, self.count)
        super(Tag, self).testPrint()

    def getTemplate(self):
        return self.site.lookup.get_template(util.tplFile('home'))

    @property
    def permalink(self):
        return self.site.generateUrl(self.exportDir, self.tag_slug)

    @property
    def exportDir(self):
        return 'tag/%s' % self.tag_slug

    @property
    def exportBasename(self):
        return ['index', 'page-%d']        
