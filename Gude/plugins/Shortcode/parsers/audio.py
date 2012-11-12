# -*- coding: utf-8 -*-
import urllib, random
def parse(site, kwargs):
    src = kwargs.get('src')
    if not src:
        return 'ERROR: audio shortcode'
    rand = '%d' % random.uniform(1000, 100000000000)
    playr_url = site.getUrl('assets/audioplayer.swf')
    return ('<object type="application/x-shockwave-flash" data="' + playr_url+ '" width="290" height="24" id="audioplayer' + rand + '">'
        + '<param name="movie" value="' + playr_url + '" />'
        + '<param name="FlashVars" value="playerID=' + rand + '&amp;bg=0xCDDFF3&amp;leftbg=0x357DCE&amp;lefticon=0xF2F2F2&amp;rightbg=0x357DCE'
        + '&amp;rightbghover=0x4499EE&amp;righticon=0xF2F2F2&amp;righticonhover=0xFFFFFF&amp;text=0x357DCE&amp;slider=0x357DCE&amp;track=0xFFFFFF'
        + '&amp;border=0xFFFFFF&amp;loader=0x8EC2F4&amp;soundFile=' + urllib.quote(src) + '" />'
        + '<param name="quality" value="high" /><param name="menu" value="false" /><param name="wmode" value="transparent" />'
        + '</object>')