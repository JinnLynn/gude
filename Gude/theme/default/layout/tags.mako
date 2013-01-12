<%inherit file="base.mako"/>
<%block name="head_title">Tags at ${site.siteTitle}</%block>
<div class="page-main tags">
    <div class="entry-head"><h1>Tags</h1></div>
    <div class="clear"></div>
% for tag in tags:
        <a href="${tag.permalink}" title="${tag.count} Posts" rel="tag">${tag.name}<span>[${tag.count} ]</span></a>
% endfor
</div><!-- .page .tags -->