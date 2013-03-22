<%def name="outputCategoryList(article)">
    % for cate in article.category:
        <a href="${cate.permalink}" title="View all posts in ${cate.name}" rel="category tag">${cate.name}</a>
    % endfor
</%def>

<%def name="pagenavi(bundle)">
    <div id="pagenavi">
        <span class="pages">Page ${bundle.curPageNum } of ${bundle.totalPageNum}</span>
    % if bundle.curPageNum < bundle.totalPageNum:
        <a href="${bundle.getPagePermalink(bundle.curPageNum+1)}" class="nav-older">Older</a>
    % endif
    % if bundle.curPageNum > 1:
        <a href="${bundle.getPagePermalink(bundle.curPageNum-1)}" class="nav-newer">Newer</a>
    % endif
    </div><!-- #pagenavi -->
</%def>