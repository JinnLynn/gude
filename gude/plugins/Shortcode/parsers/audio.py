# -*- coding: utf-8 -*-
import urllib, random

def parse(args):
    src = args.get('src')
    site = args.get('gude_site')
    rand = args.get('gude_unique')
    if not src:
        return 'ERROR: audio shortcode'
    playr_url = site.getAsset('audioplayer.swf')
    return ('<object type="application/x-shockwave-flash" data="' + playr_url+ '" width="290" height="24" id="audioplayer' + rand + '">'
        + '<param name="movie" value="' + playr_url + '" />'
        + '<param name="FlashVars" value="playerID=' + rand + '&amp;bg=0xCDDFF3&amp;leftbg=0x357DCE&amp;lefticon=0xF2F2F2&amp;rightbg=0x357DCE'
        + '&amp;rightbghover=0x4499EE&amp;righticon=0xF2F2F2&amp;righticonhover=0xFFFFFF&amp;text=0x357DCE&amp;slider=0x357DCE&amp;track=0xFFFFFF'
        + '&amp;border=0xFFFFFF&amp;loader=0x8EC2F4&amp;soundFile=' + urllib.quote(src) + '" />'
        + '<param name="quality" value="high" /><param name="menu" value="false" /><param name="wmode" value="transparent" />'
        + '</object>')