# -*- coding: utf-8 -*-

import os, shutil, codecs

import yaml

import util
from setting import *

class Publisher(object):

    def __init__(self, site):
        self.site = site

    def clean(self):
        self.forceInitGitRepo()
        self.publish(force=True)

    def publish(self, **kwargs):
        if not self.checkGit():
            return

        pub_type = self.getPublishType()
        print('Publish Type: %s' % pub_type)
        force = kwargs.get('force', False)

        pub_map = { 'git'       : lambda: self.publishByGit(force),
                    'gitftp'    : lambda: self.publishByGitFtp(force),
                    'rsync'     : lambda: self.publishByRsync()
        }

        # 准备分支
        is_cur_branch = False
        for l in os.popen('git branch').readlines():
            if l.strip(' \n') == ('* %s' % self.publishBranch):
                is_cur_branch = True
                break
        if not is_cur_branch:
            os.system('git branch -M %s > /dev/null' % self.publishBranch)

        if pub_map.has_key(pub_type):
            pub_map[pub_type]()
        else:
            print('unsupported publish type.')

    def publishByGit(self, force=False):
        remote = self.site.getConfig('git_remote');
        if not remote:
            print 'config git_remote not found.'
            return
        
        option = '-u'
        option += '' if not force else 'f'
        cmd = 'git push %s "%s" %s' % (option, remote, self.publishBranch)
        ret = os.system(cmd)
        self.publishResult(ret, cmd, '%s %s' % (remote, self.publishBranch))

    def publishByGitFtp(self, force=False):
        server = self.site.getConfig('ftp_server')
        subdir = self.site.getConfig('ftp_subdirectory')
        usr = self.site.getConfig('ftp_usr')
        pwd = self.site.getConfig('ftp_pwd')
        server_path = os.path.join(server, subdir)
        server_str = '-u "%s" -p "%s" "%s"' % (usr, pwd, server_path)
        option = ''
        if force:
            # 强制 先上传当前的GIT SHA1到log(防止此时服务器是未git ftp init的状态)
            #      然后上传所有文件
            os.system('git ftp catchup %s' % server_str)
            option = '-a'
        cmd = 'git ftp push %s %s' % (option, server_str)
        ret = os.system(cmd)
        self.publishResult(ret, cmd, server)

    def publishByRsync(self):
        data = { 'opt'      : '-av --force --ignore-errors --delete --exclude ".git"',
                 'server'   : self.site.getConfig('rsync_server'),
                 'subdir'   : self.site.getConfig('rsync_subdirectory'),
                 'usr'      : self.site.getConfig('rsync_usr'),
                 'sshkey'   : self.site.getConfig('rsync_sshkey'),
                 'src'      : self.site.deployPath.rstrip('/') + '/'
                }
        cmd = 'rsync {opt} -e "ssh -i {sshkey}" {src} {usr}@{server}:{subdir}'.format(**data)
        ret = os.system(cmd)
        self.publishResult(ret, cmd, data['server'])

    def publishResult(self, ret, cmd, server):
        data = { 'server': server, 'cmd': cmd }
        if ret == 0:
            print( 'publish [{server}] success'.format(**data) )
        else:
            print( 'publish [{server}] fail. command: {cmd}'.format(**data) )

    def checkGit(self):
        if not util.isCommandExists('git'):
            print 'GIT is non-existent'
            return False
        if not os.path.isdir('.git'):
            self.forceInitGitRepo()
        os.system('git add . && git commit -am "update at %s"' % util.toUTCISO8601())
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

    def getPublishType(self):
        return self.site.getConfig('publish_type', 'none').lower()

    @property
    def publishBranch(self):
        # 项目页 gh-pages 其它 master
        return 'gh-pages' if self.site.isGitHubProjectPage else 'master'
        