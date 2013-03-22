<%namespace name="funcs" file="functions.mako" />
<%inherit file="base.mako"/>
<%block name="head_title">Category ${bundle.name} - ${site.siteTitle}</%block>
% for article in articles:
<div id="post-${article.unique}" class="post post-list post-${article.status}">
    <div class="entry-head">
        <h1><a href="${article.permalink}" title="${article.title}" rel="bookmark">${article.title}</a></h1>
        <p class="entry-date" title="${article.date.strftime('%Y-%m-%d %H:%M:%S')}">
            <span class="day">${article.date.strftime('%d')}</span>
            <span class="month">${article.date.strftime('%b')}</span>
        </p>
    </div><!-- .entry-header -->
    <div class="entry-content">
<!-- content start -->
${article.outputSummary()}
<!-- content end -->
    </div><!-- .entry-content -->
    <div class="entry-meta">
        <ul>
            <li class="entry-author">Posted by ${article.author}</li>
            <li class="entry-categories"> in ${funcs.outputCategoryList(article)}</li>
            <li class="entry-human-time-diff"> on ${article.date.strftime('%b %d, %Y')}</li>
            <li class="entry-comments"> with <a href="${article.permalink}#comments" title="Comment on ${article.title}">Comments</a></li> 
        </ul>
    </div><!-- .entry-meta -->
</div><!-- #post-${article.unique} -->
% endfor

${funcs.pagenavi(bundle)}