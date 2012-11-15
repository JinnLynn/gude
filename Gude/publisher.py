# -*- coding: utf-8 -*-

import os,shutil

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

    def publish(self, **kwargs):
        pub_type = self.getPublishType()
        print 'Publish Type: %s' % pub_type
        force = kwargs.get('force', False)
        if pub_type == PT_GIT:
            self.publishByGit(force=force)
        elif pub_type == PT_GITFTP:
            self.publishByGitFtp(force=force)
            pass

    def publishByGit(self, force=False):
        if not self.checkGit():
            return
        remote = self.site.config.get('git_remote', '');
        if not remote:
            print 'config git_remote not found'
            return
        
        option = '-u'
        option += '' if not force else 'f'
        os.system('git push %s "%s" master' % (option, remote) )

    def publishByGitFtp(self, force=False):
        if not self.checkGit():
            return

        server = self.site.config.get('ftp_server', '')
        usr = self.site.config.get('ftp_usr', '')
        pwd = self.site.config.get('ftp_pwd', '')
        server_str = '-u "%s" -p "%s" "%s"' % (usr, pwd, server)
        option = ''
        if force:
            # 强制 先上传当前的GIT SHA1到log(防止此时服务器是未git ftp init的状态)
            #      然后上传所有文件
            os.system('git ftp catchup %s' % server_str)
            option = '-a'
        os.system('git ftp push %s %s' % (option, server_str))

    def checkGit(self):
        if not self.isCommandExists('git'):
            print 'GIT is non-existent'
            return False
        if not os.path.exists('.git') or not os.path.isdir('.git'):
            self.forceInitGitRepo()
        os.system('git add .')
        os.system('git commit -am "update"')
        return True

    def forceInitGitRepo(self):
        if os.path.exists('.git'):
            shutil.rmtree('.git')
        os.system('git init')

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
        