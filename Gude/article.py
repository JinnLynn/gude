# -*- coding: utf-8 -*-
import sys, os, codecs, time
from datetime import datetime

import yaml, feedgenerator

import util
from setting import *

# unlisted 可选关键词
# 首页包括标签与分类页  Sitemap   存档页      Feed
# home               sitemap   archives   feed

# status 可选关键词
# 置顶在archives sitemap feed页无效
#                       已发布(默认)  置顶      草稿
ARTICLE_STATUS_LIST = ['publish',   'sticky', 'draft']


""" 单篇文章 """
class Article(object):
    
    def __init__(self, site, source):
        self.site = site
        self.source = source

        # 文章配置的默认值
        self.layout     = self.site.defaultLayout
        self.title      = 'untitled'
        self.date       = util.fileCreateDate(self.source)
        self.modify     = util.fileModifyDate(self.source)
        self.author     = self.site.siteAuthor
        self.tag        = []
        self.category   = []
        self.custom     = {}
        self.unlisted   = []
        self.status     = 'publish'

        self.content = ''
        self.summary = ''

        self.unique = ''

    def parse(self):
        if not os.path.exists(self.source):
            util.logWarning( 'file non-existent. [%s]', self.source )
            return False

        fp = codecs.open(self.source, 'r', encoding='utf-8')
        lines = fp.readlines()

        # 解析文章信息
        config_str = ''
        config = {}
        index = 1

        # 解析文章配置
        try:
            # 日志配置 必须从第一行开始 支持使用<!-- --> 或 --- ---包含
            first_line = lines[0]
            if not first_line.startswith('<!--'):
                util.logWarning( "invalid article: config error '%s'", self.site.getRelativePath(self.source) )
                return False

            for line in lines[1:]:
                index += 1
                if line.startswith('-->'):
                    break
                config_str += line
            config.update( yaml.load(config_str) )
        except Exception, e:
            util.logWarning( "invalid article: config error '%s'", self.site.getRelativePath(self.source) )
            return False
        
        self.title      = config.get('title',       self.title)
        self.date       = config.get('date',        self.date)
        self.tag        = config.get('tag',         self.tag)
        self.category   = config.get('category',    self.category)
        self.layout     = config.get('layout',      self.layout)
        self.author     = config.get('author',      self.author)
        self.modify     = config.get('modify',      self.modify)
        self.custom     = config.get('custom',      self.custom)
        self.unlisted   = config.get('unlisted',    self.unlisted)
        self.status     = config.get('status',      self.status);

        self.category = self.standardizeListConfig(self.category)
        self.tag      = self.standardizeListConfig(self.tag)
        self.unlisted = self.standardizeListConfig(self.unlisted)

        try:
            self.status = self.status.lower();
        except Exception, e:
            self.status = str(self.status).lower()

        # 草稿 且 不是本地模式
        if self.isDraft():
            util.logWarning( "draft: '%s'", self.site.getRelativePath(self.source) )
            if not self.site.isLocalMode:
                return False

        # 检查date
        if not self.checkDateAvailable():
            util.logWarning( "invalid article: date error '%s'", self.site.getRelativePath(self.source) )
            return False

        # 时间超出现在的文章
        if self.date > datetime.now():
            util.logWarning( "date out: [%s] %s", (str(self.date), self.site.getRelativePath(self.source)) )
            return False

        # 不列出的文章
        if len(self.unlisted):
            util.logInfo( "unlisted in [%s]: '%s'", ', '.join(unicode("'" + s + "'") for s in self.unlisted if s), self.site.getRelativePath(self.source) )

        # 检查修改时间
        if self.modify < self.date:
            self.modify = self.date

        # 唯一标识码 发布时间时间戳的后5位
        self.unique = ('%d' % util.timestamp(self.date))[-5:]

        # 解析分类 标签
        self.parseCategory()
        self.parseTag()
        
        # 获取内容
        self.content = ''
        self.summary = ''
        for line in lines[index:]:
            # 类似 <!--more--> 的标示
            line_strip = line.strip(' \t\r\n')
            if line_strip.find('<!--') == 0 and line_strip.find('more') and line_strip.find('-->'):
                self.summary = self.content
                line = '<span id="more-%s"></span>\n' % self.unique
            self.content += line

        self.content.strip('\n\t ')
        self.summary.strip('\n\t ')

        if len(self.content) == 0:  #? 都不会成立，总是会有一个类似换行的东西 又不是\n WHY?
            util.logWarning( "invalid article: content empty '%s'", self.site.getRelativePath(self.source) )
            return False
        
        self.content = self.contentFilter(self.content)
        self.summary = self.contentFilter(self.summary) if self.summary else self.content

        # 草稿 标题加前缀
        if self.isDraft():
            self.title = '__DRAFT__ ' + self.title

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
        return True

    # 检查配置 尝试转换成list
    def standardizeListConfig(self, cfg):
            if isinstance(cfg, list):
                return cfg;
            elif isinstance(cfg, str) or isinstance(cfg, unicode):
                return map(lambda s:s.strip(), cfg.split(','))
            return []

    # 检查文章分类的有效性 只有在网站配置'category'中存在了才可用
    # 对象转换为Category对象
    def parseCategory(self):
        cate = []
        for c in self.category:
            category = self.site.convertToConfigedCategory(c)
            if category:
                if category not in cate:
                    cate_obj = Category(self.site, category)
                    cate.append(cate_obj)
                else:
                    util.logInfo( "category: '%s' already exists IN '%s'", c, self.site.getRelativePath(self.source) )
            else:
                util.logWarning( "unavailable category: '%s' IN %s", c, self.site.getRelativePath(self.source) )
        self.category = cate

    def parseTag(self):
        tag = []
        for t in self.tag:
            if t:
                tag_obj = Tag(self.site, t)
                tag.append(tag_obj)
        self.tag = tag

    def export(self):
        util.logInfo( '  %s' % self.site.getRelativePath(self.source) )
        data = {'site': self.site, 'article': self}
        self.site.exportFile(self.exportFilePath, self.layout, data)

    @property
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
        return '%s#more-%s' % (self.permalink, self.unique)

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
        try:
            # 尝试解析日期前缀 如果成功则返回去除日期的 否则为原始
            datetime.strptime(source_basename[0:ARTICLE_FILENAME_PREFIX_LEN], ARTICLE_FILENAME_PREFIX_FORMAT)
            return source_basename[ARTICLE_FILENAME_PREFIX_LEN:] 
        except Exception, e:
            pass
        return source_basename

    def getCustomData(self, key):
        return self.custom.get(key, '')

    def outputSummary(self, text='Read more...', format='<p>%s</p>', css='more-link'):
        if self.summary == self.content:
            return self.content
        more_link = '<a href="%s" class="%s">%s</a>' % (self.morePermalink, css, text)
        return self.summary + '\n' + format % more_link

    def contentFilter(self, content):
        if self.isMarkdown:
            content = util.markdown(content)
        filters = self.site.contentFilter;
        for f in filters:
            #if True:
            try:
                mod = __import__(f)
                content = getattr(mod, 'parse')(content, gude_site=self.site, gude_article=self)
            except:
                util.logWarning( 'content filter fail: %s', f )
        return content

    def exportSitemap(self):
        if self.isListed('sitemap'):
            self.site.sitemap.addUrl(self.permalink, lastmod = self.modify)

    def isListed(self, key):
        return False if key in self.unlisted else True

    def isDraft(self):
        return self.status == 'draft'

    def isPublish(self):
        return self.isSticky() or self.status == 'publish' or self.status not in ARTICLE_STATUS_LIST

    def isSticky(self):
        return self.status == 'sticky'

# 被指定生成文件的日志
class DesignatedArticle(Article):
    def __init__(self, site, source, designated):
        super(DesignatedArticle, self).__init__(site, source)
        self.designated = designated
        util.logInfo( 'designated: %s => %s', source, self.designated )

    def export(self):    
        util.logInfo( '  %s [Designated]' % self.site.getRelativePath(self.source) )
        data = {'site': self.site, 'article': self}
        self.site.exportFile(self.exportFilePath, self.layout, data)

    @property
    def permalink(self):
        return self.site.generateUrl(self.exportDir, self.exportBasename, isfile=True) 

    @property
    def exportFilePath(self):
        return self.site.generateDeployFilePath(self.exportDir, self.exportBasename, assign=True) 

    @property
    def exportDir(self):
        dirname, basename = os.path.split(self.designated)
        return dirname

    # 此时包括后缀
    @property
    def exportBasename(self):
         dirname, basename = os.path.split(self.designated)
         return basename 
        

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
    def __init__(self, site, articles):
        self.site = site
        self.articles = articles

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

        self.sortArticles()

        paged_articles = self.getPagedArticles()
        total_page_num = self.totalPageNum

        for i in range(1, total_page_num + 1):
            articles = paged_articles[i - 1]
            deploy_file = self.site.generateDeployFilePath(self.exportDir, page=i)
            self.curPageNum = i
            data = {'site': self.site, 'articles': articles, 'bundle': self}
            self.site.exportFile(deploy_file, self.templateName, data)

    def printSelf(self):
        pass

    # 对文章排序
    def sortArticles(self):
        self.sortByDateDESC()
        self.sortBySticky()

    # 按日期倒序排序
    def sortByDateDESC(self):
        self.articles = sorted(self.articles, key = lambda a: a.date, reverse = True )

    # 置顶处理
    def sortBySticky(self):
        self.articles = sorted(self.articles, key = lambda a: a.isSticky(), reverse = True)

    @property
    def count(self):
        return len(self.articles)

    @property
    def permalink(self):
        return self.site.generateUrl(self.exportDir)

    def getPagePermalink(self, page_num):
        assert 0 < page_num <= self.totalPageNum, 'page number must in 1 - %d' % self.totalPageNum
        if page_num == 1:
            return self.permalink
        return self.site.generateUrl(self.exportDir, 'page', page_num)

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
            end = start + self.numPerPage
            if i == total - 1:
                paged.append( self.articles[start:] )
            else:
                paged.append( self.articles[start:end] )
        return paged

    def exportSitemap(self):
        # 根据页面中最新日志获得更新时间
        lastmod = None
        for a in self.articles:
            if not lastmod or lastmod < a.date:
                lastmod = a.date
        for i in xrange(1, self.totalPageNum + 1):
            self.site.sitemap.addUrl(self.getPagePermalink(i), lastmod = lastmod)

    def cleanUnListed(self, key):
        self.articles = filter(lambda a: a.isListed(key), self.articles)

class Archives(ArticleBundle):
    """ 存档 存档页 文章单页的输出 """
    def __init__(self, site, articles):
        super(Archives, self).__init__(site, articles)
        self.cleanUnListed('archives')

    def printSelf(self):
        util.logInfo( 'Archives:' )

    def sortArticles(self):
        # 不关心置顶
        self.sortByDateDESC()

    @property
    def templateName(self):
        return 'archives'

    @property
    def exportDir(self):
        return 'archives'

    @property
    def numPerPage(self):
        return self.site.numPerPageInArchive;

class Home(ArticleBundle):
    """ 首页的输出 """
    def __init__(self, site, articles):
        super(Home, self).__init__(site, articles)
        self.cleanUnListed('home')

    def printSelf(self):
        util.logInfo( 'Home: %s', self.permalink )

    @property
    def templateName(self):
        return 'home'

    def exportSitemap(self):
        # 更新时间永远是站点导出时间
        for i in xrange(1, self.totalPageNum + 1):
            self.site.sitemap.addUrl(self.getPagePermalink(i))

class Feed(ArticleBundle):
    """ Feed的输出 """
    def __init__(self, site, articles):
        super(Feed, self).__init__(site, articles)
        self.cleanUnListed('feed')

    # 忽略输出方法
    def export(self):

        self.sortByDateDESC()

        num = self.site.numInFeed;
        articles = []
        if len(self.articles) >= num:
            articles = self.articles[0:num]
        else:
            articles = self.articles[0:]

        feed = feedgenerator.Atom1Feed( title = self.site.siteTitle,
                                        link = self.site.siteUrl,
                                        feed_url = self.site.feedUrl,
                                        description = self.site.siteTagline)
        item_count = 0
        for article in self.articles:
            item_count += 1
            feed.add_item(  title = article.title,
                            link = article.permalink,
                            description = article.summary,
                            pubdate = article.date)
            if item_count >= self.site.numInFeed:
                break
        
        '''
        feed = RSS2Gen.RSS2(
            title = self.site.siteTitle,
            link = self.site.siteUrl,
            description = self.site.siteTagline,
            lastBuildDate = datetime.now(),
            items = [ a.getFeedItem() for a in articles ],
            generator = util.self()
            )
        '''
        filename = self.site.generateDeployFilePath(self.site.feedFilename, assign=True)
        with open(filename, 'w') as fp:
                feed.write(fp, 'utf-8')

class Tags(ArticleBundle):
    """标签"""
    def __init__(self, site, articles):
        super(Tags, self).__init__(site, articles)
        self.cleanUnListed('home')
        self.tags = self.fetchAllTags()

    def fetchAllTags(self):
        tags = {}
        for article in self.articles:
            for tag in article.tag:
                slug = util.generateSlug(tag.name)
                if slug in tags.keys():
                    tags[slug].addArticle(article)
                else:
                    tags[slug] = Tag(self.site, tag.name)
                    tags[slug].addArticle(article)
        
        return tags.values()

    def export(self):
        self.printSelf()
        
        if self.count == 0:
            return

        # 按文章数排序
        self.tags = sorted(self.tags, key=lambda a: a.count, reverse = True)

        data = {'site': self.site, 'tags': self.tags}
        deploy_file = self.site.generateDeployFilePath('tags')

        self.site.exportFile(deploy_file, self.templateName, data)

        # 输出标签单页
        map(lambda t: t.export(), self.tags)

    def printSelf(self):
        util.logInfo( 'Tags: %s', self.permalink )

    @property
    def count(self):
        return len(self.tags)

    @property
    def exportDir(self):
        return 'tags'

    @property
    def templateName(self):
        return 'tags'

    def exportSitemap(self):
        map(lambda t: t.exportSitemap(), self.tags)

class Tag(ArticleBundle):
    """标签 
    标签页的输出
    """
    def __init__(self, site, tag):
        super(Tag, self).__init__(site, [])
        self.name = tag

    def printSelf(self):
        util.logInfo( 'Tag: %s %d %s', self.name, self.count, self.permalink )

    @property
    def templateName(self):
        return 'tag'

    @property
    def exportDir(self):
        return 'tag/%s' % self.name

class Categories(ArticleBundle):
    """分类"""
    def __init__(self, site, articles):
        super(Categories, self).__init__(site, articles)
        self.cleanUnListed('home')
        self.categories = self.fetchAllCategories()


    def fetchAllCategories(self):
        categories = {}
        for article in self.articles:
            for category in article.category:
                category_name = category.name
                # 分类是否满足条件在 文章对象中处理
                slug = util.generateSlug(category_name)
                if slug in categories.keys():
                    categories[slug].addArticle(article)
                else:
                    categories[slug] = Category(self.site, category_name)
                    categories[slug].addArticle(article)
        # 按文章数排序
        return sorted(categories.values(), cmp = lambda a, b: a.count > b.count)

    def export(self):
        self.printSelf()
        if not self.count:
            return
        map(lambda c: c.export(), self.categories)

    def printSelf(self):
        util.logInfo( 'Categories: %s', self.permalink )
    
    @property
    def count(self):
        return len(self.categories)

    def exportSitemap(self):
        map(lambda c: c.exportSitemap(), self.categories)

class Category(ArticleBundle):
    """ 分类 """
    def __init__(self, site, category):
        super(Category, self).__init__(site, [])
        self.name = category

    def printSelf(self):
        util.logInfo( 'Category: %s %d %s', self.name, self.count, self.permalink )

    @property
    def templateName(self):
        return 'category'

    @property
    def exportDir(self):
        return 'category/%s' % self.name

class Sitemap(object):
    # 模板
    SM_CONTENT_TPL = """
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    <!-- %d pages -->
%s
</urlset>"""
    SM_UPL_TPL = """
    <url>
        <loc>%s</loc>
        <lastmod>%s</lastmod>
    </url>"""

    def __init__(self, site):
        self.site = site
        self.urls = []

    def addUrl(self, loc, lastmod = None, changefreq = 'monthly', priority = '0.5'):
        if not loc:
            return
        if not isinstance(lastmod, datetime):
            lastmod = datetime.now()
        lastmod = lastmod.strftime('%Y-%m-%dT%X')
        url = util.parseTemplateString(self.SM_UPL_TPL, (loc, lastmod))
        self.urls.append(url)

    def export(self):
        page_count = len(self.urls)
        url_str = '\n'.join(unicode(s) for s in self.urls if s)
        content = util.parseTemplateString(self.SM_CONTENT_TPL, (page_count, url_str))
        util.logInfo( 'Sitemap:' )
        export_file = self.site.generateDeployFilePath('sitemap.xml', assign=True)
        with open(export_file, 'w') as fp:
            fp.write(content)
        util.logInfo( '    => %s', self.site.getRelativePath(export_file) )