<%namespace name="funcs" file="functions.mako"/>
<!doctype html>
<!--[if lt IE 7 ]><html class="ie ie9below ie6"><![endif]-->
<!--[if IE 7 ]><html class="ie ie9below ie7"><![endif]-->
<!--[if IE 8 ]><html class="ie ie9below ie8"><![endif]-->
<!--[if IE 9 ]><html class="ie ie9"><![endif]-->
<!--[if (gte IE 9)|!(IE)]><!--><html> <!--<![endif]-->
<head>
    <title><%block name="head_title">${site.siteTitle}</%block></title>
    <meta charset="UTF-8">
    <link rel="apple-touch-icon" href="${site.getAsset('images/apple-touch-icon.png')}"/>
    <link rel="shortcut icon" type="image/x-icon" href="${site.getAsset('images/favicon.ico')}" />
    <link rel="stylesheet" type="text/css" href="${site.getAsset('style.css')}" />
    <link rel="alternate" type="application/atom+xml" href="${site.feedUrl}" />
    <!-- <link rel='canonical' href="" /> -->
    <meta name="robots" content="index,follow" />
    <!-- <meta name="keywords" content="" /> -->
</head>
<body>

<div id="wrapper">
    <div id="gradient"></div><!-- #gradient -->
    <div id="header">
        <div id="menu">
            <ul>
% for menu in site.getHeaderMenu():
                <li><a href="${menu['url']}"><span>${menu['title']}</span></a></li>
% endfor
            </ul>
        </div>
    </div><!-- ＃header -->

<div id="main">
    <div id="tools-box">
        <ul>
            <li id="tool-search">
                <form action="http://google.com/search" method="get">
                    <input class="search" type="text" name="q" results="0" placeholder="Search"/>
                    <input type="hidden" name="q" value="site:${site.siteNetworkLocation}" />
                </form>
            </li>
        </ul>
    </div><!-- #tools-box -->

<div id="container">
    <div id="content" role="main">
${self.body()}   
    </div><!-- #content -->
</div><!-- #container -->

<div id="sidebar">
</div><!-- #sidebar -->

</div><!-- #main -->

<div id="footer">
    <div id="footer-left">
        2012 Powered By <a href="http://jeeker.net/projects/gude/" title="a simple python static website generator">Gude</a> &#38; <a href="http://jeeker.net/" title="Jeeker">Vellum</a>. 
        Licensed under <a href="http://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>.
    </div><!-- #footer-left -->
    <div id="footer-right">
    </div><!-- #footer-right -->
</div><!-- #footer -->

</div><!-- #wrapper -->

<!-- print javascript -->
<script type="text/javascript" src="${site.getAsset('script/action.js')}"></script>
<!--[if lt IE 9]>
<script type='text/javascript' src='${site.getAsset('script/css3-mediaqueries.js')}'></script>
<![endif]-->

${site.getSiteTrackCode()}

</body>
</html>