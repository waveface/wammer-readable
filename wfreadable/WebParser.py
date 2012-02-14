import lxml.html
import opengraph
import os
from urlparse import urlparse
import re

class WebParser(object):
    def __init__(self, html=None, url=None):
        self.html = html
        self.url = url

    def fix_relative_url(self, fetch_url, tag_url):
        urlparts = urlparse(fetch_url)
        if (urlparts.scheme == ''):
            url_base = 'http://' + urlparts.netloc
        else:
            url_base = urlparts.scheme + '://' + urlparts.netloc

        uri_path = os.path.dirname(urlparts.path)

        regex = "(http|https|ftp)://.*"
        pattern = re.compile(regex)

        if not pattern.match(tag_url):
            if tag_url[0] == '/':
                return "{0}{1}".format(url_base,  tag_url)
            else:
                return "{0}{1}/{2}".format(url_base,  uri_path,  tag_url)
        return tag_url

    def parse(self):
        result = {}

        result['url'] = self.url
        result['type'] = 'html'
        result['images'] = []
        
        p = urlparse(self.url)
        if p:
            result['provider'] = p.netloc

        og = opengraph.OpenGraph()
        og.parser(self.html)
        if og.is_valid():
            if 'description' in og:
                result['description'] = og['description']
            if 'title' in og:
                result['title'] = og['title']
            if 'url' in og:
                result['url'] = og['url']   
            if 'site_name' in og:
                result['site_name'] = og['site_name']
            if 'video' in og:
                result['videos'] = []

                video = {}
                video['url'] = og['video']
                video['height'] = og['video:height']
                video['width'] = og['video:width']

                result.append(video)
            if 'type' in og:
                result['type'] = og['type']
            if 'image' in og:
                img = {}
                img['url'] = og['image']
                img['type'] = 'cover'
                if 'image:height' in og:
                    img['height'] = og['image:height']
                if 'image:width' in og:
                    img['width'] = og['image:width']
                result['images'].append(img)
                    
        tree = lxml.html.fromstring(self.html)       

        if 'title' not in result:
            tags = tree.xpath('//title | //TITLE')
            for t in tags:
                result['title'] = t.text
                break

        tags = tree.xpath('//meta | //META')
        for t in tags:
            name = t.get('name')
            if name is None:
                continue

            name = name.lower()
            if 'description' not in result:
                if name == 'description':
                    result['description'] = t.get('content')

            if name == 'keywords':
                result['keywords'] = t.get('content')

#        imgs = tree.xpath("//img | //IMG")
#        for img in imgs:
#            src = img.get('src')
#            if src is not None:
#                result['images'].append({'url': self.fix_relative_url(result['url'], src) })

        links = tree.xpath("//link | //LINK")
        for l in links:
            rel = l.get('rel')
            if rel is None:
                continue
            rel = rel.lower()
            if rel == 'shortcut icon':
                href = l.get('href')
                if href is not None:
                    result['favicon'] = self.fix_relative_url(result['url'], href)
            elif rel == 'image_src':
                href = l.get('href')
                if href is not None:
                    result['images'].append({'url': self.fix_relative_url(result['url'], href), 'type': 'cover' })

        return result

