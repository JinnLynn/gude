# -*- coding: utf-8 -*-
import sys, os, codecs, random
from datetime import datetime

import yaml
import PyRSS2Gen.PyRSS2Gen as RSS2Gen 

import util
from setting import *

"""
文章信息

layout   : 布局名称
title    : 标题
date     : 发布时间
tags     : 标签
category : 分类

source   : 原始文件名
content  : 内容
"""

""" 单篇文章 """
class Article(object):
    
    def __init__(self, site, source):
        self.site = site
        self.source = source

        self.layout = 'post'
        self.title = 'untitled'
        self.date = None
        self.author = self.site.siteAuthor
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
        index = 1
        for line in lines[1:]:
            index += 1
            if line.find('---') == 0:
                break
            config_str += line
        config.update( yaml.load(config_str) )
        
        self.layout     = config.get('layout', self.site.defaultLayout)
        self.title      = config.get('title', 'untitled')
        self.author     = config.get('author', self.site.siteAuthor)
        self.date       = config.get('date', None)
        self.tag        = config.get('tag', [])
        self.category   = config.get('category', [])
        self.metadata   = config.get('metadata', {})

        # 检查date
        if not self.checkDateAvailable():
            print "invalid article: date error '%s'" % self.site.getRelativePath(self.source)
            return False

        # 检查分类
        self.checkCategoryAvailable()
        
        # 获取内容
        self.content = ''
        self.summary = ''
        for line in lines[index:]:
            if line.strip(' \t').find('<!--more-->') == 0:
                self.summary = self.content
                line = '<span id="more-%s"></span>' % self.unique
            self.content += line

        self.content.strip('\n\t ')
        self.summary.strip('\n\t ')

        if len(self.content) == 0:  #? 都不会成立，总是会有一个类似换行的东西 又不是\n WHY?
            print "invalid article: content empty '%s'" % self.site.getRelativePath(self.source)
            return False

        # 处理 html 与 markdown 格式
        if self.isMarkdown():
            self.content = util.markdown(self.content)
            self.summary = util.markdown(self.summary)

        # 摘要
        if not self.summary:
            self.summary = self.content

        return True

    # 文章日期是否有效
    def checkDateAvailable(self):
        if isinstance(self.date, datetime):
            return True
        if not self.date or not isinstance(self.date, str): 
            return False
        date = None
        for p in ARTICLE_DATE_FORMAT:
            try:
                date = datetime.strptime(self.date, p)
            except Exception, e:
                continue
            else:
                self.date = date
                break
        if not isinstance(self.date, datetime):
            return False
        if self.date > datetime.now():
            return False
        return True

    # 检查文章分类的有效性 只有在网站配置'category'中存在了才可用
    def checkCategoryAvailable(self):
        cate = []
        for c in self.category:
            category = self.site.convertToConfigedCategory(c)
            if category:
                if category not in cate:
                    cate.append(category)
                else:
                    print "category: '%s' already exists IN '%s'" % (c, self.site.getRelativePath(self.source))
            else:
                print "unavailable category: '%s' IN %s" % (c, self.site.getRelativePath(self.source))
        self.category = cate

    def export(self):    
        print '  %s' % self.site.getRelativePath(self.source)
        data = {'site': self.site, 'article': self}
        self.site.exportFile(self.exportFilePath, self.layout, data)

    def isMarkdown(self):
        extension = os.path.splitext(self.source)[1][1:]
        return extension.find('md') == 0 or extension.find('markdown') == 0

    # 永久链接  
    @property
    def permalink(self):
        return self.site.generateUrl(self.exportDir, self.exportBasename)

    # 跳转到 more 的链接
    @property
    def morePermalink(self):
        return '%s#%s' % (self.permalink, self.unique)

    # 导出文件的绝对路径
    @property
    def exportFilePath(self):
        return self.site.generateDeployFilePath(self.exportDir, self.exportBasename)

    @property
    def exportDir(self):
        #! 当 self.source 包括子文件夹时使用自身 如果没有则统一放入article目录
        dirname, basename = os.path.split(self.source)
        dirname = dirname[len( self.site.articlePath )+1:].strip(' /')
        if not dirname:
            dirname += 'article'
        return dirname

    # 源文件的文件名（不包括后缀）
    @property
    def exportBasename(self):
        source_basename = os.path.splitext(os.path.split(self.source)[1])[0]
        if self.site.isArticleFilenameUseDatePrefix:
            return source_basename[ARTICLE_FILENAME_PREFIX_LEN:]  
        return source_basename

    def getFeedItem(self):
        return RSS2Gen.RSSItem(
            title = self.title, 
            link = self.permalink, 
            guid = RSS2Gen.Guid(self.permalink),
            description = self.summary,
            pubDate = self.date,
            #categories = tags, 
            )

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

class ArticleBundle(object):
    """文章集合
    有多篇文章集合的处理  存档 首页 分类 标签
    """
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
        self.printSelf()

        if self.count <= 0:
            return

        self.sortByDateDESC()

        paged_articles = self.getPagedArticles()
        total_page_num = self.totalPageNum

        for i in range(1, total_page_num + 1):

            articles = paged_articles[i - 1]
            deploy_file = self.site.generateDeployFilePath(self.exportDir, page=i)

            self.curPageNum = i
            data = {'site': self.site, 'articles': articles}
            self.site.exportFile(deploy_file, self.templateName, data)

    def printSelf(self):
        return

    # 按日期倒序排序
    def sortByDateDESC(self):
        self.articles = sorted(self.articles, key = lambda a: a.date, reverse = True ) 
        pass

    @property
    def count(self):
        return len(self.articles)

    @property
    def permalink(self):
        return self.site.generateUrl(self.exportDir)

    def getPagePermalink(self, page_num):
        assert 0 < page_num <= self.totalPageNum, 'page number must in 1 - %d' % self.totalPageNum
        return self.site.generateUrl(self.exportDir, page_num)

    @property
    def templateName(self):
        return ''

    # 输出目录 相对deploy
    @property
    def exportDir(self):
        return ''

    # 每页文章数目
    @property
    def numPerPage(self):
        return self.site.numPerPage

    @property
    def totalPageNum(self):
        count = len(self.articles) / self.numPerPage;
        if len(self.articles) % self.numPerPage > 0:
            count += 1
        return count

    def getPagedArticles(self):
        paged = []
        total = self.totalPageNum
        for i in range(0, total):
            start = self.numPerPage * i
            if i == total - 1:
                paged.append( self.articles[start:] )
            else:
                paged.append( self.articles[start:self.numPerPage] )
        return paged

class Archive(ArticleBundle):
    """ 存档 存档页 文章单页的输出 """
    def __init__(self, site, articles):
        super(Archive, self).__init__(site)
        self.articles = articles

    def printSelf(self):
        print 'Archive:'

    @property
    def templateName(self):
        return 'archive'

    @property
    def exportDir(self):
        return 'archive'

    @property
    def numPerPage(self):
        return self.site.numPerPageInArchive;

class Home(ArticleBundle):
    """ 首页的输出 """
    def __init__(self, site, articles):
        super(Home, self).__init__(site)
        self.articles = articles

    def printSelf(self):
        print 'Home: %s' % self.permalink

    @property
    def templateName(self):
        return 'home'

class Category(ArticleBundle):
    """ 分类 """
    def __init__(self, site, category):
        super(Category, self).__init__(site)
        self.category_name = category

    def printSelf(self):
        print 'Category: %s %d %s' % (self.category_name, self.count, self.permalink)

    @property
    def templateName(self):
        return 'category'

    @property
    def exportDir(self):
        return 'category/%s' % self.category_name

class Tag(ArticleBundle):
    """标签 
    标签页的输出
    """
    def __init__(self, site, tag):
        super(Tag, self).__init__(site)
        self.tag_name = tag

    def printSelf(self):
        print 'Tag: %s %d %s' % (self.tag_name, self.count, self.permalink)

    @property
    def templateName(self):
        return 'tag'

    @property
    def exportDir(self):
        return 'tag/%s' % self.tag_name

class Feed(ArticleBundle):
    """ Feed的输出 """
    def __init__(self, site, articles):
        super(Feed, self).__init__(site)
        self.articles = articles

    # 忽略输出方法
    def export(self):

        self.sortByDateDESC()
        num = self.site.numInFeed;
        articles = []
        if len(self.articles) >= num:
            articles = self.articles[0:num]
        else:
            articles = self.articles[0:]

        feed = RSS2Gen.RSS2(
            title = self.site.siteTitle,
            link = self.site.siteUrl,
            description = self.site.siteTagline,
            lastBuildDate = datetime.now(),
            items = [ a.getFeedItem() for a in articles ],
            generator = util.self()
            )

        filename = self.site.generateDeployFilePath(self.site.feedFilename, assign=True)
        with open(filename, 'w') as fp:
                feed.write_xml(fp, 'utf-8')

class Tags(ArticleBundle):
    """标签"""
    def __init__(self, site, articles):
        self.site = site
        self.articles = articles
        self.tags = self.fetchAllTags()

    def fetchAllTags(self):
        tags = {}
        for article in self.articles:
            for tag in article.tag:
                slug = util.generateSlug(tag)
                if slug in tags.keys():
                    tags[slug].addArticle(article)
                else:
                    tags[slug] = Tag(self.site, tag)
                    tags[slug].addArticle(article)
        # 按文章数排序
        return sorted(tags.values(), cmp = lambda a, b: a.count > b.count)

    def export(self):
        self.printSelf()
        
        if self.count == 0:
            return

        data = {'site': self.site, 'tags': self.tags}
        deploy_file = self.site.generateDeployFilePath('tags')

        self.site.exportFile(deploy_file, self.templateName, data)

        # 输出标签单页
        map(lambda t: t.export(), self.tags)

    def printSelf(self):
        print 'Tags: %s' % self.permalink

    @property
    def count(self):
        return len(self.tags)

    @property
    def exportDir(self):
        return 'tags'

    @property
    def templateName(self):
        return 'tags'

class Categories(ArticleBundle):
    """分类"""
    def __init__(self, site, articles):
        super(Categories, self).__init__(site)
        self.articles = articles
        self.categories = self.fetchAllCategories()


    def fetchAllCategories(self):
        categories = {}
        for article in self.articles:
            for category in article.category:
                # 分类是否满足条件在 文章对象中处理
                slug = util.generateSlug(category)
                if slug in categories.keys():
                    categories[slug].addArticle(article)
                else:
                    categories[slug] = Category(self.site, category)
                    categories[slug].addArticle(article)
        # 按文章数排序
        return sorted(categories.values(), cmp = lambda a, b: a.count > b.count)

    def export(self):
        self.printSelf()
        if not self.count:
            return
        map(lambda c: c.export(), self.categories)

    def printSelf(self):
        print 'Categories: %s' % self.permalink
    
    @property
    def count(self):
        return len(self.categories)

        