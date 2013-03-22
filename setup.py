import sys, os
from gude.setting import __version__

try:
    from setuptools import setup, find_packages, findall
    setup_params = {
        'entry_points': {
            'console_scripts': [
                'gude=gude:run'
            ],
        },
        'zip_safe': False,
    }
except ImportError:
    from distutils.core import setup

data_files = []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('gude'):
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    if filenames and not '__init__.py' in filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = "Gude",
    packages = find_packages(),
    version = __version__,
    description = "Gude is a simple static site generator, written in Python.",
    author = "JinnLynn",
    author_email = "eatfishlin@gmail.com",
    url = "http://jeeker.net/projects/gude/",
    install_requires = ['mako', 'pyyaml', 'feedgenerator', 'commando', 'markdown2'],
    data_files = data_files,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        ],
    **setup_params
    )