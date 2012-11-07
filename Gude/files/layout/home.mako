<%inherit file="base.mako"/>

% for article in articles:
<a href="${article.permalink}">${article.title}</a><br />
% endfor
