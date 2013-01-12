<%namespace name="funcs" file="functions.mako" />
<%inherit file="base.mako"/>
<%block name="head_title">Archives at ${site.siteTitle}</%block>
<div class="page-main archives">
    <div class="entry-head"><h1>Blog Archives</h1></div>
    <div class="clear"></div>
<% 
    year_articles = {}
    for article in articles:
        year = int(article.date.strftime('%Y'));
        if year_articles.has_key(year):
            year_articles[year].append(article)
        else:
            year_articles[year]=[article]
%>
% for year in year_articles.keys()[::-1]:
    <h2>${year}</h2>
    <ul>
        % for article in year_articles[year]:
        <li>
            <h4><a href="${article.permalink}" title="Permanent Link to ${article.title}" rel="bookmark">${article.title}</a></h4>
            <span class="date">${article.date.strftime('%b %d')}</span>
            <span class="cate">Posted in ${funcs.outputCategoryList(article) | trim}</span>
        </li>
        % endfor
    </ul>
    <div class="clear"></div>
% endfor
</div><!-- .archives -->

${funcs.pagenavi(bundle)}