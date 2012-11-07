# -*- coding: utf-8 -*-
import sys, os, shutil, codecs, re
from datetime import datetime

import libs.yaml as yaml
from mako.lookup import TemplateLookup

import util, setting, server
from article import Article, Tag, Category, Home
from setting import DEFAULT_CONFIG_FILE
from setting import DEFAULT_CONFIG
from setting import SCRIPT_PATH
from setting import SITE_PATH
from setting import ARTICLE_EXTENSION
from setting import ARTICLE_EXCLUDE_DIR

class Database:
    def __init__(self, site):
        self.site = site
        self.articles = Home(self.site)
        

    def add(self, article):
        self.articles.addArticle(article)

    def export(self):
        # 输出文章
        self.exportArticles()
        # 输出标签
        self.exportTags()
        # 输出分类
        self.exportCategories()
        pass

    """ 输出文章 """
    def exportArticles(self):
        # 输出文章
        self.articles.exportAllArticles()
        # 输出文章列表页 包括首页
        self.articles.export()
        pass

    """ 输出分类页 """
    def exportCategories(self):
        categories = self.fetchCategories()
        map(lambda c: c.testPrint(), categories)
        map(lambda c: c.export(), categories)
        pass

    """ 输出标签页 """
    def exportTags(self):
        tags = self.fetchTags()
        map(lambda t: t.testPrint(), tags)
        # 按标记文章数排序
        tags = sorted(tags, cmp = lambda a, b: a.count > b.count)

        data = {'site': self.site, 'tags': tags}

        template = self.site.lookup.get_template(util.tplFile('tags'))
        html = template.render_unicode(**data).strip()
        with open(os.path.join(self.site.deployPath, 'tags.html'), 'w') as f:
            f.write(html.encode('utf-8'))

        map(lambda t: t.export(), tags)

    def fetchTags(self):
        tags = {}
        for article in self.articles.articles:
            for tag in article.tag:
                slug = util.encodeURIComponent(tag)
                if slug in tags.keys():
                    tags[slug].addArticle(article)
                else:
                    tags[slug] = Tag(self.site, tag)
                    tags[slug].addArticle(article)
        return tags.values()

    def fetchCategories(self):
        categories = {}
        for article in self.articles.articles:
            for category in article.category:
                if not self.site.isValidCategory(category):
                    print 'category name "%s" in "%s" is unavailable' % (category, util.getRelativePath(article.source))
                    continue
                slug = util.encodeURIComponent(category)
                if slug in categories.keys():
                    categories[slug].addArticle(article)
                else:
                    categories[slug] = Category(self.site, category)
                    categories[slug].addArticle(article)
        return categories.values();

    def testPrint(self):
        print 'db:'
        print '    atricles:'
        for a in self.articles.articles:
            print('   ' + a.source)
            pass
        #map(lambda a: print('   ' + a.source), self.articles.articles)


class Gude(object):
    ARTICLE_PATH = lambda f: os.path.join(self.getArticlePath(), f)

    def __init__(self):
        if not os.path.exists(DEFAULT_CONFIG_FILE):
            util.die('config file [%s] is non-existent.' % DEFAULT_CONFIG_FILE)
        util.log('current time = %s' % datetime.now())
        util.log('SCRIPT_PATH = %s' % SCRIPT_PATH)
        util.log('site path = %s' % SITE_PATH)

        # 配置
        self.config = DEFAULT_CONFIG

        config_file = os.path.join(SITE_PATH, DEFAULT_CONFIG_FILE)
        with open(config_file) as f:
            for k, v in yaml.load(f).items():
                k = util.stdKey(k)
                self.config[k] = v
        util.log('site config = %s' % self.config)

        # 模板
        template_dir = os.path.join(SITE_PATH, 'layout')
        self.lookup = TemplateLookup(directories=[template_dir], input_encoding='utf-8')
        
        # 数据库
        self.db = Database(self)

    def main(self):
        subcommand = util.subcommand();
        util.log('sub command = %s' % subcommand)
        if subcommand == 'init':
            self.init()
        elif subcommand == 'build':
            self.build()
        elif subcommand == 'add':
            self.add()
        elif subcommand == 'serve':
            server.run()
        else:
            print setting.HELP_DOC
        pass

    def init(self):
        if os.listdir(SITE_PATH) and (not util.isOptExists('f')):
            util.die(u" %s is not empty" % SITE_PATH)
        # 强制 删除旧的文件
        if util.isOptExists('f'):
            for exist_file in os.listdir(SITE_PATH):
                abs_path = os.path.join(SITE_PATH, exist_file)
                shutil.rmtree(abs_path) if os.path.isdir(abs_path) else os.remove(abs_path)

        # 拷贝文件
        for src_file in os.listdir(self.staticFilePath):
            src = os.path.join(self.staticFilePath, src_file)
            dst = os.path.join(SITE_PATH, src_file)
            print src, dst
            shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy(src, dst)

    def build(self):
        # 删除发布目录
        #+ 添加判断
        if os.path.isdir(self.deployPath):
            shutil.rmtree(self.deployPath)
        os.makedirs(self.deployPath)

        # 建立所有文章的数据库
        for files in os.walk(self.articlePath):
            # 忽略的文件夹 仅关心顶层目录
            i, j = os.path.split(files[0])
            if i == self.articlePath and j in ARTICLE_EXCLUDE_DIR:
                util.log('exclude dir: %s' % files[0])
                continue

            for fname in files[2]:
                fname = os.path.join(files[0], fname)
                if not self.isValidArticleFile(fname):
                    util.log('invalid article: %s' % fname)
                    continue
                article = Article(self, fname)
                self.db.add(article) if article.parse() else util.log('invalid article: %s' % fname)  
        # 导出
        self.db.export()

    def add(self):
        filename = sys.argv[2] + ".md"
        header = setting.ARTICLE_TEMPLATE % time.date.strftime('%Y-%m-%d %H:%M:%S', datetime.now())
        article_filename = os.path.join(self.getArticlePath(), filename)
        with codecs.open(article_filename, 'w', encoding='utf-8') as fp:
            fp.write(header)

    def fetchAllArticles(self):
        def traverseDir(dir):
            pass
        #files = os.listdir(self.articlePath)
        pass
        
    def generateUrl(self, *parts, **kwargs):
        subs = [self.config['subdirectory']]
        subs.extend(parts)
        domain = self.config['domain'].strip('/')
        url = re.sub('//+', '/', '/'.join(str(s) for s in subs if s)).strip('/')
        return "%s/%s.%s" % (domain, url, self.exportFileExtension)

    def generateDeployFilePath(self, *parts, **kwargs):
        deploy_file_path = self.deployPath
        for s in parts:
            s = util.encodeURIComponent(s)
            deploy_file_path = os.path.join(deploy_file_path, s)
        return '%s.%s' % (deploy_file_path, self.exportFileExtension)

    def getPathInSite(self, filename):
        return os.path.join(SITE_PATH, filename)

    def isValidArticleFile(self, filename):
        root, ext = os.path.splitext(filename)
        if ext[1:] in ARTICLE_EXTENSION:
            return True
        return False

    # 静态文件路径
    @property
    def staticFilePath(self):
        return os.path.join(SCRIPT_PATH, 'files')

    # 原始文章路径
    @property
    def articlePath(self):
        return os.path.join(SITE_PATH, 'article')

    # 发布路径
    @property
    def deployPath(self):
        return os.path.join(SITE_PATH, 'deploy')

    # 导出文件后缀
    @property
    def exportFileExtension(self):
        return self.config.get('extension', 'html')

    # 每页文章数
    @property
    def numPerPage(self):
        return self.config['num_per_page']

    # 配置属性
    @property
    def author(self):
        return self.config['author']

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

    def isValidCategory(self, category):
        return category.lower() in map(lambda c: c.lower(), self.config['category'])

if __name__ == '__main__':
    site = Gude()
    site.main()