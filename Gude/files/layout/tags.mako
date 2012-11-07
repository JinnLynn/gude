<%inherit file="base.mako"/>

% for tag in tags:
            <a href="${tag.permalink}" title="${tag.count} Posts" rel="tag">${tag.tag_name}<span>[${tag.count} ]</span></a>
% endfor