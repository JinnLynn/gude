# -*- coding: utf-8 -*-
import sys, os

#! 强制默认编码为utf-8
reload(sys)
sys.setdefaultencoding('utf8') 

# 使用本地第三方库
from setting import SCRIPT_PATH
sys.path.insert(0, os.path.join(SCRIPT_PATH, 'libs'))
sys.path.insert(0, os.path.join(SCRIPT_PATH, 'plugins'))

from core import Gude

def run():
    Gude().run()