# -*- coding: utf-8 -*-

def parse(site, kwargs):
    # [btn url="URL_1,URL_2", title="TITTLE_1,TITLE_2", center="1"]
    style_to_class = {'large': 'btn-large', 'primary': 'btn-primary'};

    urls = kwargs.get('url', '').split(',')
    titles = kwargs.get('title', '').split(',')
    styles = kwargs.get('style', '').split(',')
    icons = kwargs.get('icon', '').split(',')
    is_center = False if str(kwargs.get('center', '1')) == '0' else True
    
    if len(urls)==0 or len(titles)==0 or len(urls) != len(titles):
        return 'ERROR: btn shortcode'
    is_group = True if len(urls) > 1 else False
    con_class = []
    con_class.append('btn-group' if is_group else 'btn-single')
    if is_center:
        con_class.append('btn-center')

    btn_class = ['btn']

    for style in styles:
        if style_to_class.has_key(style):
            btn_class.append(style_to_class[style])

    output = ''

    for i in range(0, len(urls)):
        this_btn_class = btn_class
        if len(icons) > i and icons[i]:
            this_btn_class.append('icon-%s' % icons[i])
        output += '<a href="%s" class="%s">%s</a>' % (urls[i], ' '.join(s for s in this_btn_class if s), titles[i])

    output = '<span class="%s">%s</span>' % (' '.join(s for s in con_class if s), output)
    return output