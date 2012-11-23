# -*- coding: utf-8 -*-
import re, time, random

"""
内容过滤器 支持形如 [btn url=""] 的短标签
REF: https://github.com/martey/django-shortcodes
"""
def parse(content, **kwargs):
    site = kwargs.get('site')
    ex = re.compile(r'\[(.*?)\]')
    groups = ex.findall(content)
    pieces = {}
    parsed = content

    count = 0
    try:
        unique = kwargs.get('gude_article', None).unique
    except Exception, e:
        unique = '%d' % random.uniform(10000, 99999)

    for item in groups:
        if ' ' in item:
            name, space, args = item.partition(' ')
            args = __parse_args__(args)
        # If shortcode does not use spaces as a separator, it might use equals
        # signs.
        elif '=' in item:
            name, space, args = item.partition('=')
            args = __parse_args__(args)
        else:
            name = item
            args = {}

        #if True:
        try:
            mod = import_parser('Shortcode.parsers.' + str(name).decode('utf-8'))
            function = getattr(mod, 'parse')

            # 获得一个唯一标示码
            count += 1
            args.update({'gude_unique': '%s%02d' % (unique, count)})

            args.update(kwargs)
            
            result = function(args)
            parsed = re.sub(r'\[' + re.escape(item) + r'\]', result, parsed)
        except:
            pass

    return parsed

def import_parser(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def __parse_args__(value):
    ex = re.compile(r'[ ]*(\w+)=([^" ]+|"[^"]*")[ ]*(?: |$)')
    groups = ex.findall(value)
    kwargs = {}

    for group in groups:
        if group.__len__() == 2:
            item_key = group[0]
            item_value = group[1]

            if item_value.startswith('"'):
                if item_value.endswith('"'):
                    item_value = item_value[1:]
                    item_value = item_value[:item_value.__len__() - 1]

            kwargs[item_key] = item_value

    return kwargs