# Gude 

## What is Gude?

[Gude][] is a simple static site generator, written in Python.

* Simple, very easy to use
* Work with GIT & GitHub
* Completely static output

![Gude](http://i.imgur.com/qBb5l.png)

## Installation

```
git clone git://github.com/JinnLynn/gude.git && cd gude && python setup.py install
```

## USAGE

#### create a new gude site

```
gude init [-h|-f]
```

#### configuring gude site

edit `site.yaml` for public settings and `privacy.yaml` for private settings, here are example: [site-example.yaml][] [privacy-example.yaml][]

[site-example.yaml]: https://github.com/JinnLynn/gude/blob/master/gude/docs/site-example.yaml
[privacy-example.yaml]: https://github.com/JinnLynn/gude/blob/master/gude/docs/privacy-example.yaml

#### add new article

```
gude add -t "TITLE" -f "FILENAME" [--status "STATUS"] [--layout "LAYOUT"] [--html]
```

#### build site

```
gude build [-l|--local] [-p|--preview] [--less] [--less-compress] [-i|--info]
```

#### serve site

```
gude serve [-p PORT|--port PORT] [-s|--silent]
```

#### publish site

```
gude [-c|--clean] [-f|--force] [-b|--build]
```

#### backup site

```
gude [-c|--clean] [-f|--clean] [-r|--remote]
```

## LICENSE

The MIT license.

For more information, please visit project page at http://jeeker.net/projects/gude/. 

[Gude]: http://jeeker.net/projects/gude/