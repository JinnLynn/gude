<%namespace name="funcs" file="functions.mako"/>
<%inherit file="base.mako"/>
<%block name="head_title">${article.title} at ${site.siteTitle}</%block>
<div id="post-${article.unique}" class="page post-${article.status}">
    <div class="entry-head">
        <h1>${article.title}<small>${article.getCustomData('desc')}</small></h1>
        <p class="entry-date" title="${article.date}">
            <span class="day">${article.date.strftime('%d')}</span>
            <span class="month">${article.date.strftime('%b')}</span>
        </p>
    </div><!-- .entry-header -->
    <div class="entry-content">
<!-- content start -->
${article.content}
<!-- content end -->
    </div><!-- .entry-content -->
    <div class="entry-meta">
        <ul>
            <li class="entry-author">Posted by ${article.author}</li>
            <li class="entry-categories"> in ${funcs.outputCategoryList(article)}</li>
            <li class="entry-human-time-diff"> on ${article.date.strftime('%b %d, %Y')}</li>
            <li class="entry-comments">with <a href="${article.permalink}#disqus_thread">comments</a></li>
        </ul>  
    </div><!-- .entry-meta -->
</div><!-- #post-226 -->

${site.getCommentCode(article.permalink)}
