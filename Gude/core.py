# -*- coding: utf-8 -*-
import sys, os, shutil, codecs, re
from datetime import datetime

import yaml
from mako.lookup import TemplateLookup
from commando.commando import *

import util, setting, server
from article import *
from setting import DEFAULT_CONFIG_FILE
from setting import DEFAULT_CONFIG
from setting import SCRIPT_PATH
from setting import SITE_PATH
from setting import ARTICLE_EXTENSION
from setting import ARTICLE_EXCLUDE_DIR

class Site:
    def __init__(self):
        # 配置
        self.config = DEFAULT_CONFIG

        config_file = os.path.join(SITE_PATH, DEFAULT_CONFIG_FILE)
        with open(config_file) as f:
            for k, v in yaml.load(f).items():
                k = util.stdKey(k)
                self.config[k] = v

        # 模板
        template_dir = os.path.join(SITE_PATH, 'layout')
        self.lookup = TemplateLookup(directories=[template_dir], input_encoding='utf-8')
        
        self.articles = []
        

    def add(self, article):
        if not isinstance (article, Article):
            raise ValueError, 'type of article is not Article'
        elif article in self.articles:
            raise ValueError, 'article is already exists'
        self.articles.append(article)

    def export(self):
        # 输出文章
        self.exportArticles()

        # 输出首页
        home = Home(self, self.articles)
        home.export()

        # 输出存档
        archive = Archive(self, self.articles)
        archive.export()

        # 输出分类
        categories = Categories(self, self.articles)
        categories.export()

        # 输出标签
        tags = Tags(self, self.articles)
        tags.export()

        # 输出Feed
        feed = Feed(self, self.articles)
        feed.export()

        # 输出404
        self.export404()

        # 拷贝文件
        self.copyFiles()

    def exportArticles(self):
        print 'Article:'
        map(lambda a: a.export(), self.articles)

    def export404(self):
        print '404:'
        deploy_file = self.generateDeployFilePath('404.html', assign=True)
        data = {'site': self}
        self.exportFile(deploy_file, '404', data)
        

    def exportFile(self, export_file, template_name, data):
        util.tryMakeDirForFile(export_file)
        template = None
        try:
            template = self.getTemplate(template_name)
        except Exception, e:
            pass
        assert template, "template '%s' is non-existent" % template_name
        html = template.render_unicode(**data).strip()
        with open(export_file, 'w') as fp:
            fp.write(html.encode('utf-8'))
        print "    => %s" % self.getRelativePath(export_file)

    def copyFiles(self):
        print 
        print 'Copy Files:'

        assets_path = self.generateDeployFilePath('assets', assign=True)
        print '  %s\n    => %s' % (self.getRelativePath(self.assetsPath), self.getRelativePath(assets_path))
        shutil.copytree(self.assetsPath, assets_path)
        pass

    def testPrint(self):
        print 'db:'
        print '    atricles:'
        for a in self.articles.articles:
            print('   ' + a.source)
            pass
        #map(lambda a: print('   ' + a.source), self.articles.articles)


    # 生成地址 默认: 文件夹
    def generateUrl(self, *parts, **kwargs):
        isfile = kwargs.get('isfile', False)   # 是文件？
        page = kwargs.get('page', 1)           # 分页
        assert type(page) == int and page >= 1, 'page must be INT and >= 1. '
        is_url_quoted = kwargs.get('quoted', False) # 地址已转换成url组件
        site_url = self.siteUrl;
        sub_url = util.standardizePath('/'.join(unicode(s) for s in parts if s)).strip('/')
        if not is_url_quoted:
            sub_url = util.urlQuote(sub_url)
        if page != 1:
            sub_url += '/page/%d' % page
        if isfile:
            return '%s%s' % (site_url, sub_url)
        return "%s%s/" % (site_url, sub_url.rstrip('/'))

    # 生成发布文件路径 默认: 在文件夹下生成index.html文件
    def generateDeployFilePath(self, *parts, **kwargs):
        assign = kwargs.get('assign', False) # 指定了文件名
        page = kwargs.get('page', 1)
        assert type(page) == int and page >= 1, 'page must be INT and >= 1. '
        deploy_file_path = self.deployPath
        for s in parts:
            deploy_file_path = os.path.join(deploy_file_path, util.standardizePath(s))
        if page != 1:
            deploy_file_path = os.path.join(deploy_file_path, 'page/%d' % page)
        if assign:
            return deploy_file_path
        return os.path.join(deploy_file_path, 'index.html')

    def getPathInSite(self, filename):
        return os.path.join(SITE_PATH, filename)

    def isValidArticleFile(self, filename):
        root, ext = os.path.splitext(filename)
        if ext[1:] in ARTICLE_EXTENSION:
            return True
        return False

    def getTemplate(self, name):
        return self.lookup.get_template(util.tplFile(str(name)))

    # 静态文件路径
    @property
    def staticFilePath(self):
        return os.path.join(SCRIPT_PATH, 'files')

    # 原始文章路径
    @property
    def articlePath(self):
        return os.path.join(SITE_PATH, 'content')

    # 发布路径
    @property
    def deployPath(self):
        return os.path.join(SITE_PATH, 'deploy')

    # 资源文件路径
    @property
    def assetsPath(self):
        return os.path.join(SITE_PATH, 'assets')

    @property
    def exportFeedFile(self):
        return self.config.get('feed', 'feed.rss')
        pass

    # 每页文章数
    @property
    def numPerPage(self):
        return self.config['num_per_page']

    # Feed输出的文章数量
    def numInFeed(self):
        return 10 #+ 可配置

    # 配置属性
    @property
    def siteAuthor(self):
        return self.config.get('author', '')

    @property
    def siteDomain(self):
        return '%s/' % self.config.get('domain', 'http://localhost/').strip(' /')
        
    @property
    def siteUrl(self):
        subdirectory = self.config.get('subdirectory', '').strip('/')
        subdirectory = re.sub('//+', '/', subdirectory)
        if subdirectory:
            subdirectory += '/'
        return self.siteDomain + subdirectory

    @property
    def siteTitle(self):
        return self.config.get('title', '')

    @property
    def siteTagline(self):
        return self.config.get('tagline', '')
        pass

    @property
    def siteCategories(self):
        return self.config.get('category', [])

    # 相对原始文章目录的路径
    def getRelativePathWithArticle(self, abspath):
        assert abspath.find(self.articlePath) == 0, 'path error. %s' % abspath
        return abspath[len(self.articlePath)+1:]

    # 相对发布目录的路径
    def getRelativePathWithDeploy(self, abspath):
        assert abspath.find(self.deployPath) == 0, 'path error. %s' % abspath
        return abspath[len(self.deployPath)+1:]

    # 相对站点目录路径
    def getRelativePath(self, abspath):
        assert abspath.find(SITE_PATH) == 0, 'path error. %s' % abspath
        return abspath[len(SITE_PATH)+1:]

    def convertToConfigedCategory(self, category):
        for cate in self.siteCategories:
            if category.lower() == cate.lower():
                return cate
        return None


class Gude(Application):
    ARTICLE_PATH = lambda f: os.path.join(self.getArticlePath(), f)

    def __init__(self):

        if not os.path.exists(DEFAULT_CONFIG_FILE):
            util.die('config file [%s] is non-existent.' % DEFAULT_CONFIG_FILE)

        self.site = Site()

    def run(self, args=None):
        super(Gude, self).run(args)

    @command(description='Gude - a simple python static website generator', 
        epilog='Use %(prog)s {command} -h to get help on individual commands')
    @version('-v', version='%(prog)s ' + setting.VERSION)
    def main(self, args):
        pass

    @subcommand('init', help='Create a new site.')
    @true('-f', '--force', default=False, dest='overwrite', help='Overwrite the current site if it exists')
    def init(self, args):
        if os.listdir(SITE_PATH) and (not util.isOptExists('f')):
            util.die(u" %s is not empty" % SITE_PATH)
        # 强制 删除旧的文件
        if args.overwrite:
            for exist_file in os.listdir(SITE_PATH):
                abs_path = os.path.join(SITE_PATH, exist_file)
                shutil.rmtree(abs_path) if os.path.isdir(abs_path) else os.remove(abs_path)

        # 拷贝文件
        for src_file in os.listdir(self.staticFilePath):
            src = os.path.join(self.staticFilePath, src_file)
            dst = os.path.join(SITE_PATH, src_file)
            print src, dst
            shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy(src, dst)

    @subcommand('build', help='build a new site.')
    @version('-f', default=False, dest='overwrite')
    def build(self, args):
        # 删除发布目录
        #+ 添加判断
        if os.path.isdir(self.site.deployPath):
            shutil.rmtree(self.site.deployPath)
        os.makedirs(self.site.deployPath)

        # 建立所有文章的数据库
        for files in os.walk(self.site.articlePath):
            # 忽略的文件夹 仅关心顶层目录
            i, j = os.path.split(files[0])
            if i == self.site.articlePath and j in ARTICLE_EXCLUDE_DIR:
                util.log('exclude dir: %s' % files[0])
                continue

            for fname in files[2]:
                fname = os.path.join(files[0], fname)
                if not self.site.isValidArticleFile(fname):
                    util.log('invalid article: %s' % fname)
                    continue
                article = Article(self.site, fname)
                self.site.add(article) if article.parse() else util.log('invalid article: %s' % fname)  
        # 导出
        self.site.export()

    @subcommand('add', help='add new article')
    @store('-n', '-name', default='', dest='filename', help='filename')
    @true('--html', default=False, dest='is_html', help='HTML type')
    def add(self, args):
        if not args.filename:
            print 'fail'
            return
        extension = '.md'
        if args.is_html:
            extension = '.html'
        filename = args.filename + extension
        #+ 检查文件是否存在 文件名相同即有问题 后缀不重要
        header = setting.ARTICLE_TEMPLATE % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        article_filename = os.path.join(self.articlePath, filename)
        with codecs.open(article_filename, 'w', encoding='utf-8') as fp:
            fp.write(header)

    @subcommand('serve', help='Serve the website')
    @store('-p', '--port', type=int, default=8910, dest='port', help='The port where the website must be served from.')
    def serve(self, args):
        server.run(args.port)


if __name__ == '__main__':
    Gude().run()