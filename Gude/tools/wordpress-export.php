<?php 
/**
 * Wordpress to Gude 导出工具
 */

require('./wp-blog-header.php');

// 输出目录
define('EXPORT_DIR', 'export');

// 是否输出不经过处理的原始内容
define('EXPORT_ORIGINAL', false);

// 输出的格式 注意 只是输出文件后缀 不影响内容
// Gude支持md、html后缀的文件，并通过它区分文件类型
define('EXPORT_FORMAT', 'html');

$template = "<!--
title:      '%title%'
date:       %date%
author:     '%author%'
layout:     '%layout%'
category:   [%category%]
tag:        [%tag%]
-->
%content%
";

$query = new WP_Query();
$query->query( array( 'post_type'       => array('post', 'page'),
                      'posts_per_page'  => 100000 )
              );

function getCategory() {
    global $query, $post;
    $category = array();
    foreach ( get_the_category() as $cate ) {
        $category[] = "'" . $cate->name . "'";
    }
    return implode(',', $category);
}

function getTag() {
    $tags = get_the_tags();
    if ($tags === false) {
        return '';
    }
    $tags_a = array();
    foreach ($tags as $tag) {
        $tags_a[] = "'" . $tag->name . "'";
    }
    return implode(',', $tags_a);
}

while ($query->have_posts()) {
    global $post;
    $query->the_post();

    $layout = $post->post_type;
    $title = get_the_title();
    $date = get_the_date('Y-m-d H:m:s');
    $author = get_the_author();
    $content = get_the_content();
    if (!EXPORT_ORIGINAL) {
        $content = apply_filters('the_content', $content);
        $content = str_replace(']]>', ']]&gt;', $content);
    }

    $category = getCategory();
    $tag = getTag();

    $filename = $post->post_name;

    $search =  array( "%layout%", "%title%", "%date%", "%author%", "%category%", "%tag%", "%content%");
    $replace = array( $layout,    $title,    $date,    $author,    $category,    $tag,    $content  );
    $export = str_replace( $search, $replace, $template );

    if (!is_dir(EXPORT_DIR)) {
        mkdir(EXPORT_DIR);
    }

    $path = EXPORT_DIR . '/' . get_the_date('Y-m-d') . '-' . $filename . '.' . EXPORT_FORMAT;
    file_put_contents($path, $export);

    echo $title . '<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=> ' . $path . '<br /><br />';

}

?>