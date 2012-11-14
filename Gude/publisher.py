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

    def publish(self):
        pub_type = self.getPublishType()
        print 'Publish Type: %s' % pub_type
        if pub_type == PT_GIT:
            self.publishByGit()
        elif pub_type == PT_GITFTP:
            self.publishByGitFtp()
            pass

    def publishByGit(self):
        if not self.isCommandExists('git'):
            print 'GIT is non-existent'
            return
        remote = self.site.config.get('git_remote', '');
        if not remote:
            print 'config git_remote not found'
            return

        if not os.path.exists('.git') or not os.path.isdir('.git'):
            self.forceInitGitRepo()
        os.system('git add .')
        os.system('git commit -am "update"')
        os.system('git push -f "%s" master' % remote)

    def publishByGitFtp(self, init=False):
        if self.getPublishType() is not PT_GITFTP:
            print 'publish type is not %s' % PT_GITFTP
            return
        if not self.isCommandExists('git'):
            print 'GIT is non-existent'
            return
        if not os.path.exists('.git') or not os.path.isdir('.git'):
            self.forceInitGitRepo()
        os.system('git add .')
        os.system('git commit -am "update"')

        server = self.site.config.get('ftp_server', '')
        usr = self.site.config.get('ftp_usr', '')
        pwd = self.site.config.get('ftp_pwd', '')
        cmd = 'init' if init else 'push'
        os.system('git ftp %s -u "%s" -p "%s" "%s"' % (cmd, usr, pwd, server))

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
        