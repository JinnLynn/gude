# -*- coding: utf-8 -*-
import sys, os, shutil, codecs, re
from datetime import datetime

import yaml
from mako.lookup import TemplateLookup
from commando.commando import *

import util, server
from article import *
from setting import *
from publisher import *

class Site:
    def __init__(self):
        # 配置
        self.config = DEFAULT_CONFIG
        self.isDevelopMode = False

        try:
            config_file = os.path.join(SITE_PATH, DEFAULT_CONFIG_FILE)
            with open(config_file) as f:
                for k, v in yaml.load(f).items():
                    k = util.stdKey(k)
                    self.config[k] = v           
        except:
            pass
        
        self.articles = []
        self.lookup = None

    def checkDir(self):
        if not os.path.exists(DEFAULT_CONFIG_FILE):
            util.die('config file [%s] is non-existent.' % DEFAULT_CONFIG_FILE)

    def build(self):
        # 删除发布目录
        if not os.path.isdir(self.deployPath):
            os.makedirs(self.deployPath)
        for f in os.listdir(self.deployPath):
            if f in DEPLOY_UNDELETE_FILES:
                continue
            abs_path = self.generateDeployFilePath(f, assign = True)
            if os.path.isdir(abs_path):
                shutil.rmtree(abs_path)
            if os.path.isfile(abs_path):
                os.remove(abs_path)

        # 索引所有的文章
        self.indexAllArticles()

        # 导出
        self.export()
        pass

    def indexAllArticles(self):
        self.articles = []
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
                designated = self.getDesignated(fname)
                article = Article(self, fname) if not designated else DesignatedArticle(self, fname, designated)
                if not article.parse():
                    continue
                self.articles.append(article)

    def export(self):
        # 输出文章
        self.exportArticles()

        # 输出首页
        home = Home(self, self.articles)
        home.export()

        # 输出存档
        archives = Archives(self, self.articles)
        archives.export()

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
        print_info = lambda f,t: '  %s\n    => %s' % (f, t)
        print '\nCopy Files:'

        assets_path = self.generateDeployFilePath('assets', assign=True)
        print print_info('assets', self.getRelativePath(assets_path))
        shutil.copytree(self.assetsPath, assets_path)

        files = self.config.get('file_copy', {})
        if not isinstance(files, dict):
            print "config 'file_copy' Error"
            return

        for f in files.keys():
            if not os.path.exists(f):
                print "file '%s' is non-existent" % f
                continue
            to_file = os.path.join(self.deployPath, files[f]) # 保留指定的文件大小写 不能用generateDeployFilePath
            if os.path.exists(to_file):
                print "file '%s' is already exists" % self.getRelativePath(to_file)
                continue
            if os.path.isfile(f):
                shutil.copy(f, to_file)
            elif os.path.isdir(f):
                shutil.copytree(f, to_file)
            print print_info(f, self.getRelativePath(to_file))
        

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
        url = "%s%s" % (site_url, sub_url)
        return url.rstrip('/') + '/'

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

    def getUrl(self, filepath):
        filepath.lstrip('/')
        return self.siteUrl + filepath.lstrip('/')

    def getPathInSite(self, filename):
        return os.path.join(SITE_PATH, filename)

    def isValidArticleFile(self, filename):
        root, ext = os.path.splitext(filename)
        if ext[1:] in ARTICLE_EXTENSION:
            return True
        return False

    def getTemplate(self, name):
        if not self.lookup:
            self.lookup = TemplateLookup(directories=[self.layoutPath], input_encoding='utf-8')
        return self.lookup.get_template(util.tplFile(str(name)))

    # 原始文章路径
    @property
    def articlePath(self):
        return os.path.join(SITE_PATH, 'content')

    # 发布路径
    @property
    def deployPath(self):
        return os.path.join(SITE_PATH, 'deploy')

    # 网站主题路径
    # 站点工作目录 => 脚本目录
    @property
    def themePath(self):
        cur_theme = self.config.get('theme', 'default')
        theme_path = os.path.join(SITE_PATH, 'theme', cur_theme)
        if os.path.isdir(theme_path):
            return theme_path
        theme_path = os.path.join(SCRIPT_PATH, 'theme', cur_theme)
        if os.path.isdir(theme_path):
            return theme_path
        util.die('theme [%s] is non-existent.' % cur_theme)

    # 资源文件路径
    @property
    def assetsPath(self):
        return os.path.join(self.themePath, 'assets')

    @property
    def layoutPath(self):
        return os.path.join(self.themePath, 'layout')

    @property
    def feedFilename(self):
        return self.config.get('feed_filename', 'feed.rss')

    # 每页文章数
    @property
    def numPerPage(self):
        return self.config['num_per_page']

    # 存档页文章数
    @property
    def numPerPageInArchive(self):
        return self.config.get('num_in_archive', 50)

    # Feed输出的文章数量
    def numInFeed(self):
        return self.config.get('num_in_feed', 10)

    # 配置属性
    @property
    def siteAuthor(self):
        return self.config.get('author', '')

    # 默认layout
    @property
    def defaultLayout(self):
        return self.config.get('default_layout', 'post')  

    @property
    def siteDomain(self):
        default = 'http://localhost/'
        domain = self.config.get('domain', default) if not self.isDevelopMode else self.config.get('dev_domain', default)
        return '%s/' % domain.strip(' /')
        
    @property
    def siteUrl(self):
        return self.productionEnvSiteUrl if not self.isDevelopMode else self.developEnvSiteUrl

    # 生产环境下的网站地址
    @property
    def productionEnvSiteUrl(self):
        return self.getSiteUrl_('domain', 'subdirectory')

    @property
    def developEnvSiteUrl(self):
        return self.getSiteUrl_('dev_domain', 'dev_subdirectory')

    def getSiteUrl_(self, domain_key, sub_dir_key):
        domain = self.config.get(domain_key, 'http://localhost/').strip(' /')
        subdir = self.config.get(sub_dir_key, '')
        subdir = re.sub('//+', '/', subdir.strip('/'))
        if subdir:
            subdir += '/'
        return '%s/%s' %(domain, subdir)
        pass

    @property
    def feedUrl(self):
        return self.siteUrl + self.feedFilename.lstrip('/')
        pass

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

    @property
    def isArticleFilenameUseDatePrefix(self):
        return self.config.get('filename_date_prefix', True)

    @property
    def disgusShortname(self):
        return self.config.get('disgus_shortname', '')

    @property
    def contentFilter(self):
        return self.config.get('content_filter', [])
        pass

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

    def getDesignated(self, source):
        designated = self.config.get('designated', {})
        if not isinstance(designated, dict):
            return None
        source = self.getRelativePathWithArticle(source)
        dist = designated.get(source, None)
        if dist:
            print 'designated: %s => %s' % (source, dist)
        return dist


class Gude(Application):
    ARTICLE_PATH = lambda f: os.path.join(self.getArticlePath(), f)

    def __init__(self):
        self.site = Site()

    def run(self, args=None):
        super(Gude, self).run(args)

    @command(description='Gude - a simple python static website generator', 
        epilog='Use %(prog)s {command} -h to get help on individual commands')
    @version('-v', version='%(prog)s ' + VERSION)
    def main(self, args):
        pass

    @subcommand('init', help='Create a new site.')
    @true('-f', '--force', default=False, dest='force', help='Overwrite the current site if it exists')
    def init(self, args):
        # 目录下存在文件
        if os.listdir(SITE_PATH):
            if not args.force:
                util.die(u" %s is not empty" % SITE_PATH)
            else:
                confirm = raw_input('remove all files? yes OR no:')
                if confirm == 'yes':
                    for exist_file in os.listdir(SITE_PATH):
                        abs_path = os.path.join(SITE_PATH, exist_file)
                        shutil.rmtree(abs_path) if os.path.isdir(abs_path) else os.remove(abs_path)
                else:
                    return

        for d in SITE_INCLUDE_DIR:
            os.makedirs(d)

        with codecs.open(DEFAULT_CONFIG_FILE, 'w', encoding='utf-8') as fp:
            fp.write(SITE_CONFIG_TEMPLATE)

        print 'everything is ready.'


    @subcommand('build', help='build a new site.')
    @true('-f', default=False, dest='overwrite')
    @true('-p', '--preview', default=False, dest='preview', help='start webserver after builded.')
    @true('-d', '--devmode', default=False, dest='devmode', help='build in develop mode')
    def build(self, args): 
        self.site.isDevelopMode = args.devmode
        self.site.checkDir()
        self.startBuild()
        if args.preview:
            self.startServer(DEFAULT_SERVER_PORT)

    @subcommand('add', help='add new article')
    @store('-t', default='Untitled', dest='title', help='article title')
    @store('-f', default='', dest='filename', help='article filename, no extension')
    @store('-d', default='', dest='dirname', help='article directory')
    @store('-l', default='', dest='layout' )
    @true('--html', default=False, dest='is_html', help='Use HTML type, default is Markdown')
    def add(self, args):
        self.site.checkDir()

        if not args.filename and not args.title:
            print 'something error'
            return

        if not args.filename:
            args.filename = util.standardizePath(args.title)
        # 检查文件是否存在 文件名相同即有问题 后缀不重要
        if self.isBasenameExists(args.filename, args.dirname):
            print 'filename is already exists'
            return
        filename = args.filename
        filename += '.html' if args.is_html else '.md' 
        if self.site.isArticleFilenameUseDatePrefix:
            filename = '%s%s' % (datetime.now().strftime(ARTICLE_FILENAME_PREFIX_FORMAT), filename)
        abspath = os.path.join(self.site.articlePath, args.dirname, filename)
        if not args.layout:
            args.layout = self.site.defaultLayout
        
        header = ARTICLE_TEMPLATE % (args.layout, args.title, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        with codecs.open(abspath, 'w', encoding='utf-8') as fp:
            fp.write(header)
        print "article '%s' created." % self.site.getRelativePath(abspath)

    @subcommand('serve', help='Serve the website')
    @store('-p', '--port', type=int, default=DEFAULT_SERVER_PORT, dest='port', help='The port where the website must be served from.')
    def serve(self, args):
        self.startServer(args.port)

    @subcommand('publish', help='Publish the website')
    @true('-c', default=False, dest='clean', help='Clean git repo if use Git to publish')
    @true('--initgitftp', default=False, dest='initgitftp', help='init git ftp')
    def publish(self, args):
        self.site.checkDir()
        publisher = Publisher(self.site)
        os.chdir(self.site.deployPath)
        if args.clean:
            publisher.clean()
        elif args.initgitftp:
            publisher.publishByGitFtp(init=True)
        else:
            publisher.publish()

    def startBuild(self):
        self.site.build()

    def startServer(self, port):
        httpd_ = server.Server(self, port)
        try:
            print('Webserver [http://localhost:%d] starting...' % port)
            httpd_.serve_forever()
        except KeyboardInterrupt, SystemExit:
            print('\nReceived shutdown request. Shutting down...')
            httpd_.shutdown()
            print('Server successfully stopped')
            exit()

    def isBasenameExists(self, basename, dirname):
        abs_dir = os.path.join( self.site.articlePath, dirname)
        if not os.path.isdir(abs_dir):
            os.makedirs(abs_dir)
            print "directory '%s' created." % self.site.getRelativePath(abs_dir)
        for f in os.listdir(abs_dir):
            base, extionsion = os.path.splitext(f)
            if self.site.isArticleFilenameUseDatePrefix:
                base = base[ARTICLE_FILENAME_PREFIX_LEN:]
            if base == basename:
                return True
        return False

if __name__ == '__main__':
    Gude().run()