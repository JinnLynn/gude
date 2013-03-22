# -*- coding: utf-8 -*-
import sys, os, shutil, re, urllib, logging
import urlparse
from datetime import datetime
from glob import glob

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
        self.isLocalMode = False

        try:
            config_file = self.getPathInSite(DEFAULT_CONFIG_FILE)
            if os.path.isfile(config_file):
                with open(config_file) as f:
                    self.config.update( yaml.load(f) )

            privacy_config_file = self.getPathInSite(DEFAULT_PRIVACY_CONFIG_FILE)
            if os.path.isfile(privacy_config_file):
                with open(privacy_config_file) as f:
                    self.config.update( yaml.load(f) )
        except:
            util.logError('site config load fail')
        
        self.articles = []
        self.lookup = None
        self.sitemap = Sitemap(self)

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
                util.logInfo('exclude dir: %s' % files[0])
                continue

            for fname in files[2]:
                fname = os.path.join(files[0], fname)
                if not self.isValidArticleFile(fname):
                    util.logInfo('invalid article: %s' % fname)
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

        # 输出Sitemap
        map(lambda a: a.exportSitemap(), self.articles)
        map(lambda s: s.exportSitemap(), [home, archives, categories, tags])
        self.sitemap.export()

        # 拷贝文件
        self.copyFiles()

    def exportArticles(self):
        util.logInfo( 'Article:' )
        map(lambda a: a.export(), self.articles)

    def export404(self):
        util.logInfo( '404:' )
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
        # 编码问题 不能用 util.writeToFile
        with open(export_file, 'w') as fp:
            fp.write(html.encode('utf-8'))
        util.logInfo( '    => %s', self.getRelativePath(export_file) )

    def copyFiles(self): 
        print_info = lambda f,t: '  %s\n    => %s' % (f, t)
        util.logInfo( 'Copy Files:' )

        assets_path = self.generateDeployFilePath('assets', assign=True)
        util.logInfo( print_info('assets', self.getRelativePath(assets_path)) )
        shutil.copytree(self.assetsPath, assets_path)

        copy_files = self.getConfig('file_copy', [])
        if not isinstance(copy_files, list):
            util.logWarning( "config 'file_copy' Error" )
            return

        for cfg in copy_files:
            src = cfg.get('src', None)
            dst = cfg.get('dst', None)
            if not src or not dst:
                continue
            src = os.path.join('static', src)
            from_files = glob(src)
            if not len(from_files):
                util.logWarning( "file '%s' is non-existent" % src )
                continue
            to_file = os.path.join(self.deployPath, dst) # 保留指定的文件大小写 不能用generateDeployFilePath
            if os.path.exists(to_file) and not os.path.isdir(to_file):
                util.logWarning( "file '%s' is already exists" % self.getRelativePath(to_file) )
                continue
            for from_file in from_files:  
                if os.path.isfile(from_file):
                    shutil.copy2(from_file, to_file)
                elif os.path.isdir(from_file):
                    to_file_dir = os.path.join(to_file, os.path.basename(from_file))
                    util.copytree(from_file, to_file_dir)
                util.logInfo( print_info(from_file, self.getRelativePath(to_file)) )
    
    def parseLESS(self, is_compress):
        if not util.isCommandExists('lessc'):
            util.die('lessc is non-existent.')
        if not os.path.exists(os.path.join(self.themePath, 'less', 'style.less')):
            util.die('style.less is non-existent.');
        cmd = 'lessc {} {} {}'.format(
            '--yui-compress' if is_compress else '',
            os.path.join(self.themePath, 'less', 'style.less'), 
            os.path.join(self.assetsPath, 'style.css')
            )
        os.system(cmd)

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
        is_url_quoted = kwargs.get('quoted', False)  # 地址已转换成url组件
        site_url = self.siteUrl
        try:
            sub_url = '/'.join(str(s) for s in parts if s)
        except:
            sub_url = '/'.join(unicode(s) for s in parts if s)
        finally:
            sub_url = util.standardizePath(sub_url).strip('/')

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
        assign = kwargs.get('assign', False)  # 指定了文件名
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
        return self.siteUrl + filepath.lstrip('/')

    def getAsset(self, filepath, buf={}):
        # 通过原始文件的修改时间获得时间戳
        org_filepath = os.path.join(self.assetsPath, filepath)
        file_hash = buf[org_filepath] if org_filepath in buf.keys() else util.fileHash( org_filepath )
        buf[org_filepath] = file_hash
        filepath = os.path.join('assets', filepath)
        url = os.path.join(self.siteUrl, filepath)
        if file_hash:
            url += '?' + file_hash[-5:]
        return url 

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

    # 获取设置
    def getConfig(self, key, default=''):
        cfg = self.config.get(key, default)
        return default if cfg is None else cfg

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
        cur_theme = self.getConfig('theme', 'default')
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
        return self.getConfig('feed_filename', 'atom.xml')

    # 每页文章数
    @property
    def numPerPage(self):
        return self.getConfig('num_per_page', 5)

    # 存档页文章数
    @property
    def numPerPageInArchive(self):
        return self.getConfig('num_in_archive', 50)

    # Feed输出的文章数量
    @property
    def numInFeed(self):
        return self.getConfig('num_in_feed', 10)

    # 配置属性
    @property
    def siteAuthor(self):
        return self.getConfig('author')

    # 默认layout
    @property
    def defaultLayout(self):
        return self.getConfig('default_layout', 'post')

    @property
    def siteDomain(self):
        default = 'http://localhost/'
        domain = self.getConfig('domain', default) if not self.isLocalMode else self.getConfig('local_domain', default)
        return '%s/' % domain.strip(' /')

    @property
    def siteUrl(self):
        return self.productionEnvSiteUrl if not self.isLocalMode else self.localEnvSiteUrl

    # 生产环境下的网站地址
    @property
    def productionEnvSiteUrl(self):
        return self.getSiteUrl_('domain', 'subdirectory')

    # 本地环境下的网站地址
    @property
    def localEnvSiteUrl(self):
        return self.getSiteUrl_('local_domain', 'local_subdirectory')

    def getSiteUrl_(self, domain_key, sub_dir_key):
        domain = self.getConfig(domain_key, 'http://localhost/').strip(' /')
        subdir = self.getConfig(sub_dir_key)
        subdir = re.sub('//+', '/', subdir.strip('/'))
        if subdir:
            subdir += '/'
        return '%s/%s' % (domain, subdir)

    @property
    def feedUrl(self):
        return self.getConfig('feed_url', self.siteUrl + self.feedFilename.lstrip('/')).strip()

    @property
    def siteTitle(self):
        return self.getConfig('title')

    @property
    def siteTagline(self):
        return self.getConfig('tagline')

    @property
    def siteCategories(self):
        return util.tryToList( self.getConfig('category', []) )

    @property
    def contentFilter(self):
        return util.tryToList( self.getConfig('content_filter', []) )

    @property
    def isGitHubProjectPage(self):
        return self.getConfig('github_project_page', False)

    @property
    def siteNetworkLocation(self):
        #return re.sub('^.*://+', '', self.siteDomain).strip('/')
        return urlparse.urlparse(self.siteUrl).netloc

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
        designated = self.getConfig('designated', [])
        if not isinstance(designated, list):
            return None
        source = self.getRelativePathWithArticle(source)
        for d in designated:
            if source == d.get('src', ''):
                return d.get('dst', None)
        return None

    # 网站跟踪代码 使用Google Analytics
    def getSiteTrackCode(self):
        track_id = self.getConfig('google_analytics_track_id')
        if not track_id:
            return '<!-- google_analytics_track_id is not configured. -->'
        return util.parseTemplateString(SITE_TRACK_TEMPLATE, track_id)

    # 评论服务类型 多说 或 disqus
    @property
    def commentService(self):
        service = self.getConfig('comment_service', 'duoshuo').lower()
        return service if service in COMMENT_TEMPLATE.keys() else 'duoshuo'
        
    # 评论代码
    def getCommentCode(self, data):
        shortname = self.getConfig('comment_service_shortname')
        if not shortname:
            return '<!-- comment_service_shortname is not configured. -->'
        if not COMMENT_TEMPLATE.has_key(self.commentService):
            return '<!-- comment template no found. -->'
        comment_data = { 'shortname'    : shortname,
                         'permalink'    : '',
                         'page-title'   : ''
                        }
        if isinstance(data, dict):
            comment_data.update(data)
        output = COMMENT_TEMPLATE[self.commentService].format(**comment_data)
        return output

    def getHeaderMenu(self):
        menus = [{'title': 'Home', 'url': self.siteUrl}]
        menus.extend( self.getConfig('header_menu', []) )
        for menu in menus:
            menu['url'] = self.getAbsoluteUrl(menu['url'])
        return menus

    def getAbsoluteUrl(self, relative_url):
        return urlparse.urljoin(self.siteUrl, relative_url)

class Gude(Application):
    ARTICLE_PATH = lambda f: os.path.join(self.getArticlePath(), f)

    def __init__(self):
        self.site = Site()

    def run(self, args=None):
        super(Gude, self).run(args)

    @command(description='Gude - a simple python static website generator', 
        epilog='Use %(prog)s {command} -h to get help on individual commands')
    @version('-v', version='Gude ' + VERSION)
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

        # 写入配置文件
        util.writeToFile(DEFAULT_CONFIG_FILE, SITE_CONFIG_TEMPLATE)
        util.writeToFile(DEFAULT_PRIVACY_CONFIG_FILE, SITE_PRIVACY_CONFIG_TEMPLATE)

        # README
        util.writeToFile('README.md', README_TEMPLATE)
        util.writeToFile('deploy/README.md', README_TEMPLATE)

        if not self.createGitRepo():
            return

        util.logAlways('everything is ready.')


    @subcommand('build', help='build a new site.')
    @true('-p', '--preview', default=False, dest='preview', help='start webserver after builded.')
    @true('-l', '--local', default=False, dest='localmode', help='build in local mode')
    @true('-i', '--info', default=False, dest='print_info', help='print export info')
    @true('--less', default=False, dest='less', help='LESS parse')
    @true('--less-compress', default=False, dest='less_compress', help='LESS parse with compress')
    def build(self, args):
        if args.print_info:
            util.logLevelSet(logging.NOTSET)
        self.site.isLocalMode = args.localmode
        self.site.checkDir()
        if args.less_compress or args.less:
            self.site.parseLESS(args.less_compress)
        self.startBuild()
        if args.preview:
            self.startServer(DEFAULT_SERVER_PORT)

    @subcommand('add', help='add new article')
    @store('-t', default='Untitled', dest='title', help='article title')
    @store('-f', default='', dest='filename', help='article filename, no extension')
    @store('--status', default='', dest='status', help='article status')
    @store('--layout', default='', dest='layout'  )
    @true('--html', default=False, dest='is_html', help='Use HTML type, default is Markdown')
    def add(self, args):
        self.site.checkDir()

        if not args.filename and not args.title:
            util.logError( 'something error.' )
            return

        dirname, filename = os.path.split(args.filename);

        if not filename:
            filename = util.standardizePath(args.title)

        # 检查文件是否存在 文件名相同即有问题 后缀不重要
        if self.isBasenameExists(dirname, filename):
            util.logError( 'filename is already exists.' )
            return

        append_info = ''
        if args.layout:
            append_info += '\nlayout:     %s' % args.layout
        if args.status:
            append_info += '\nstatus:     %s' % args.status

        filename += '.html' if args.is_html else '.md' 
        filename = '%s%s' % (datetime.now().strftime(ARTICLE_FILENAME_PREFIX_FORMAT), filename)
        abspath = os.path.join(self.site.articlePath, dirname, filename)
        args.title = args.title.decode('utf-8')
        header = ARTICLE_TEMPLATE % (args.title, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), append_info)
        util.writeToFile(abspath, header)
        util.logAlways( "article '%s' created.", self.site.getRelativePath(abspath) )

    @subcommand('serve', help='Serve the website')
    @store('-p', '--port', type=int, default=DEFAULT_SERVER_PORT, dest='port', help='The port where the website must be served from.')
    @true('-s', '--silent', default=False, dest='silent', help='silent mode')
    def serve(self, args):
        self.startServer(args.port, args.silent)

    @subcommand('publish', help='Publish the website')
    @true('-c', default=False, dest='clean', help='Clean git repo')
    @true('-f', '--force', default=False, dest='force', help='force update')
    @true('-b', '--build', default=False, dest='build', help='build site before publish')
    def publish(self, args):
        self.site.checkDir()
        if args.build:
            self.startBuild()
        publisher = Publisher(self.site)
        os.chdir(self.site.deployPath)
        if args.clean:
            publisher.clean()
        else:
            publisher.publish(force=args.force)

    @subcommand('backup', help='Backup site with GIT')
    @true('-c', default=False, dest='clean', help='Clean git repo')
    @true('--remote', default=False, dest='remote', help='push to remote server')
    @true('-f', default=False, dest='force', help='force push')
    def backup(self, args):
        # 使用GIT备份

        # 重建Git repo
        if args.clean:
            confirm = raw_input('remove old git repo and rebuild it? yes OR no:')
            if confirm == 'yes':
                os.system('(rm -rf .git*) > /dev/null')
                self.createGitRepo()
            return

        # 提交改变
        os.system('git add . && git commit -am "backup at %s" > /dev/null' % util.toUTCISO8601())

        # 如果是GitHub项目主页 则 分支为master 否则为source
        branch = 'master' if self.site.isGitHubProjectPage else 'source'
        # 当前的分支不是想要的
        is_cur_branch = False
        for l in os.popen('git branch').readlines():
            if l.strip(' \n') == ('* %s' % branch):
                is_cur_branch = True
                break
        if not is_cur_branch:
            os.system('git branch -M %s > /dev/null' % branch)
        print 'local backup success.'
        if not args.remote:
            return
        server = self.site.getConfig('git_remote');
        force_opt = '--force' if args.force else ''
        ret = os.system('git push %s %s %s' % (force_opt, server, branch))
        print 'remote backup [%s %s] %s.' % (server, branch, 'success' if ret == 0 else 'fail')

    def startBuild(self):
        util.logAlways('Start building...')
        self.site.build()
        util.logAlways('Site build success.')

    def startServer(self, port, silent):
        try:
            httpd_ = server.Server(self, port, silent)
            if not silent:
                util.logAlways('Webserver [http://localhost:%d] starting...', port)
            httpd_.serve_forever()
        except KeyboardInterrupt, SystemExit:
            util.logAlways( '\nReceived shutdown request. Shutting down...' )
            httpd_.shutdown()
            util.logAlways('Server successfully stopped')
            util.die()
        except Exception, e:
            util.logAlways('Webserver start fail')
            util.logAlways(e)
            util.die()

    def isBasenameExists(self, dirname, basename):
        if os.path.isabs(dirname):
            util.die('error: must be a relative path');
        abs_dir = os.path.join( self.site.articlePath, dirname)
        if not os.path.isdir(abs_dir):
            os.makedirs(abs_dir)
            util.logInfo("directory '%s' created." % self.site.getRelativePath(abs_dir))
        for f in os.listdir(abs_dir):
            base, extionsion = os.path.splitext(f)
            base = base[ARTICLE_FILENAME_PREFIX_LEN:]
            if base == basename:
                return True
        return False

    def createGitRepo(self):
        if os.path.isdir('.git'):
            return True
        if not os.path.isfile('.gitignore'):
            util.writeToFile('.gitignore', GITIGNORE_SITE)
        if os.system('(git init && git add . && git commit -m "init") > /dev/null'):
            print 'create git repo fail'
            return False
        return True


if __name__ == '__main__':
    Gude().run()