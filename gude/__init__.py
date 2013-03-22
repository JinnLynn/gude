# -*- coding: utf-8 -*-
import sys, os

#! 强制默认编码为utf-8
reload(sys)
sys.setdefaultencoding('utf8')

def run():
    from core import Gude
    Gude().run()