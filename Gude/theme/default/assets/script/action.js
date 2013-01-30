(function($) {

    /**
     * jQuery Cookie Plugin by Klaus Hartl
     * https://github.com/carhartl/jquery-cookie
     */
    $.cookie = function(key, value, options) {

        // key and at least value given, set cookie...
        if (arguments.length > 1 && (!/Object/.test(Object.prototype.toString.call(value)) || value === null || value === undefined)) {
            options = $.extend({}, options);

            if (value === null || value === undefined) {
                options.expires = -1;
            }

            if (typeof options.expires === 'number') {
                var days = options.expires, t = options.expires = new Date();
                t.setDate(t.getDate() + days);
            }

            value = String(value);

            return (document.cookie = [
                encodeURIComponent(key), '=', options.raw ? value : encodeURIComponent(value),
                options.expires ? '; expires=' + options.expires.toUTCString() : '', // use expires attribute, max-age is not supported by IE
                options.path    ? '; path=' + options.path : '',
                options.domain  ? '; domain=' + options.domain : '',
                options.secure  ? '; secure' : ''
            ].join(''));
        }

        // key and possibly options given, get cookie...
        options = value || {};
        var decode = options.raw ? function(s) { return s; } : decodeURIComponent;

        var pairs = document.cookie.split('; ');
        for (var i = 0, pair; pair = pairs[i] && pairs[i].split('='); i++) {
            if (decode(pair[0]) === key) return decode(pair[1] || ''); // IE saves cookies with empty string as "c; ", e.g. without "=" as opposed to EOMB, thus pair[1] may be undefined
        }
        return null;
    };

    $.fn.jPostListSlider = function() {
        var easeTime = 600;
        var showTime = 5000;
        return this.each(function(){
            var container = $(this);
            var panel_container = container.find(".panel-container");
            var panels = panel_container.find(".panel");
            var panel_width = panels.width();
            var panel_count = panels.size();
            var viewer_width = panel_width * panel_count;
            panel_container.css("width", viewer_width);

            //create nav
            for (i=0; i<panel_count; i++)
                container.find("#post-list-nav").append('<div class="nav-item"></div>');
            
            var navs = container.find("#post-list-nav .nav-item");
            
            navs.eq(0).addClass("current");
            
            var cur_nav_item = 0;
            var slide_paused = false;
            var step = 1;
            container.hover(function(){
                slide_paused = true;
                clearInterval(AutoSlideID);
            }, function(){
                slide_paused = false;
                AutoSlideID = setInterval(function(){ AutoSlide(-1); }, showTime);
            });
            
            GetNextItem = function() {
                if (step > 0 && (cur_nav_item + step) >= panel_count)
                    step = -1;
                else if (step < 0 && (cur_nav_item + step) < 0) 
                    step = 1;
                return cur_nav_item + step;
            };

            AutoSlide = function(next) {
                next = (next < 0) ? GetNextItem() : next;
                navs.removeClass("current").eq(next).addClass("current");
                var cnt = - ( panel_width * next);
                panel_container.animate({left: cnt}, easeTime, "swing", function() {
                    panels.css('opacity', 1.0);
                });
                panels.not(panels[next]).animate({opacity: 0.0001}, easeTime * 0.6);
                panels.eq(next).animate({opacity: 1.0}, easeTime);
                cur_nav_item = next;
            };
            
            AutoSlideID = setInterval(function(){ AutoSlide(-1); }, showTime);
    
            // Tab nav
            navs.each(function(z) {
                $(this).click(function() {
                    AutoSlide(z);
                    return false;
                });
            });
        });
    };    

    //内容尺寸重置 最好在页面内容全部载入后进行
    $.fn.jContentResize = function() {
        var content_height = $("#content").height();
        var sidebar_height = $("#sidebar").height();
        if (content_height <= sidebar_height)
        {
            sidebar_height += 50;
            $("#content").height(sidebar_height);
            $("#sidebar").height(sidebar_height);
        };

    };

    $.jBrowserWarning = function(settings) {
        settings = $.extend({
                              autoHide:  true,
                              hideTime:  3600000,
                              showCount: 300
                   }, settings);
        if (!$.browser.msie || $.browser.version >= 9.0)
            return;
        if ( settings.showCount > 0)
        {
            v = $.cookie("browser-warning-count");
            count = (isNaN(v) || !v) ? 0 : parseInt(v);
            count++;
            if (count > settings.showCount)
                return;
            $.cookie("browser-warning-count", count);
        }
        var chrome = '<a href="http://www.google.com/chrome/" alt="Google Chrome">Google Chrome</a>';
        var firefox = '<a href="http://www.mozilla.org/en-US/firefox/new/" alt="Firefox">Firefox</a>';
        var safari = '<a href="http://www.apple.com/safari/" alt="Safari">Safari</a>';
        var info = "你使用的浏览器(或其内核)是IE " + $.browser.version + "，";
        info += ($.browser.version >= 9.0) 
                ? ""
                : "无法完整支持现行的网页标准，"; 
        info += "不要让别人为你的落后买单，请选择使用" + chrome + ", " + safari + "或" + firefox + "!";

        $("#wrapper").prepend('<div id="browser-warning">' + info + '</div>');

        var HideBrowserWarning = function() {
            $("#browser-warning").hide("slow");
        };
        if (settings.autoHide)
           setTimeout(HideBrowserWarning, settings.hideTime);
    };
    
    $(function() { 
        $.jBrowserWarning({showCount:-1});
        //使<p><span><img /></span></p>下的图片置中
        //$(".entry-content").find("p:has(span>img),p:has(embed)").css("text-align", "center");
        
        $("#post-list-viewer").jPostListSlider(); 

        $("#toggle-sidebar").bind("click", function() {
            if ($("#sidebar").css("display") == "none")
            {
                $("body").removeClass("single-column");
            } else {
                $("body").addClass("single-column");
            }
        });

        $("pre code").addClass("prettyprint linenums");
        var langs = new Array("css","javascript","python")
        $("pre code").each(function(){
            ele = $(this)
            for (i in langs) {
                if (ele.hasClass(langs[i])) {
                    //ele.addClass("lang-" + langs[i]);
                }
            }
        });

        //使外链在新窗口打开
        $("a:not([href*='" + window.location.host + "'])").filter("a[href^='http']").attr("target", "_blank");
    });

})(jQuery);