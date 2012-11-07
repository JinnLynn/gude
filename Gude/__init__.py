# -*- coding: utf-8 -*-
import sys, os
from setting import SCRIPT_PATH

def run():
    # 使用本地第三方库
    sys.path.insert(0, os.path.join(SCRIPT_PATH, 'libs'))

    from core import Gude
    site = Gude()
    site.main()