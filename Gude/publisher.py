# -*- coding: utf-8 -*-

import os,shutil,codecs

import yaml

import util
from setting import *

PT_GIT = 'GIT'
PT_GITFTP = 'GITFTP'
#PT_FTP = 'FTP' # 不支持
PT_UNKNOWN = 'UNKNOWN'

PTMAP = {'git': PT_GIT, 'gitftp': PT_GITFTP}

class Publisher(object):
    def __init__(self, site):
        self.site = site

    def clean(self):
        pub_type = self.getPublishType()
        if pub_type == PT_GIT or pub_type == PT_GITFTP:
            self.forceInitGitRepo()
        self.publish(force=True)

    def publish(self, **kwargs):
        pub_type = self.getPublishType()
        print 'Publish Type: %s' % pub_type
        force = kwargs.get('force', False)

        if not self.checkGit():
            return

        # 准备分支
        is_cur_branch = False
        for l in os.popen('git branch').readlines():
            if l.strip(' \n') == ('* %s' % self.publishBranch):
                is_cur_branch = True
                break
        if not is_cur_branch:
            os.system('git branch -M %s > /dev/null' % self.publishBranch)

        if pub_type == PT_GIT:
            self.publishByGit(force=force)
        elif pub_type == PT_GITFTP:
            self.publishByGitFtp(force=force)
        else:
            print 'unsupported publish type.'

    def publishByGit(self, force=False):
        remote = self.site.config.get('git_remote', '');
        if not remote:
            print 'config git_remote not found.'
            return
        
        option = '-u'
        option += '' if not force else 'f'
        ret = os.system('git push %s "%s" %s' % (option, remote, self.publishBranch) )
        print 'publish [%s %s] %s.' % (remote, self.publishBranch, 'success' if ret == 0 else 'fail')

    def publishByGitFtp(self, force=False):
        config_file = os.path.join(SITE_PATH, DEFAULT_FTP_CONFIG_FILE)
        if not os.path.isfile(config_file):
            print 'FTP config [%s] is non-existent.' % DEFAULT_FTP_CONFIG_FILE
            return
        config = {}
        try:
            with open(config_file) as f:
                for k, v in yaml.load(f).items():
                    k = util.stdKey(k)
                    config[k] = v           
        except:
            print 'FTP config [%s] parse fail.' % DEFAULT_FTP_CONFIG_FILE
            return

        server = config.get('ftp_server', '')
        usr = config.get('ftp_usr', '')
        pwd = config.get('ftp_pwd', '')
        server_str = '-u "%s" -p "%s" "%s"' % (usr, pwd, server)
        option = ''
        if force:
            # 强制 先上传当前的GIT SHA1到log(防止此时服务器是未git ftp init的状态)
            #      然后上传所有文件
            os.system('git ftp catchup %s' % server_str)
            option = '-a'
        ret = os.system('git ftp push %s %s' % (option, server_str))
        print 'publish [%s] %s.' % (server, 'success' if ret == 0 else 'fail')

    def checkGit(self):
        if not self.isCommandExists('git'):
            print 'GIT is non-existent'
            return False
        if not os.path.isdir('.git'):
            self.forceInitGitRepo()
        os.system('git add . && git commit -am "update at %s"' % util.utcNow())
        return True

    def forceInitGitRepo(self):
        if os.path.exists('.git'):
            shutil.rmtree('.git')
        if not os.path.isfile('.gitignore'):
            with codecs.open('.gitignore', 'w', encoding='utf-8') as fp:
                fp.write(GITIGNORE_DEPLOY)
        if not os.path.isfile('index.html'):
            with codecs.open('index.html', 'w', encoding='utf-8') as fp:
                fp.write('coming soon...')
        os.system('(git init && git add . && git commit -am "init") > /dev/null')

    def isCommandExists(self, program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return True
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return True

        return False

    def getPublishType(self):
        config = self.site.config.get('publish_type', 'none').lower()
        for key in PTMAP.keys():
            if key == config:
                return PTMAP[key]
        return PT_UNKNOWN

    @property
    def publishBranch(self):
        # 项目页 gh-pages 其它 master
        return 'gh-pages' if self.site.isGitHubProjectPage else 'master'
        