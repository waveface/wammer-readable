import lxml.html
from lxml.html.clean import Cleaner
import opengraph
import os
from urlparse import urlparse
import re

class WebParser(object):
    def __init__(self, html=None, url=None):
        self.html = html
        self.url = url
        self.base_url = url
        self.dom_tree = None

    def fix_relative_url(self, fetch_url, tag_url):
        urlparts = urlparse(fetch_url)
        if (urlparts.scheme == ''):
            url_base = 'http://' + urlparts.netloc
        else:
            url_base = urlparts.scheme + '://' + urlparts.netloc

        uri_path = os.path.dirname(urlparts.path)

        regex = "(http|https|ftp)://.*"
        pattern = re.compile(regex, flags=re.I)

        if not pattern.match(tag_url):
            if tag_url.startswith("//"):
                return "http:{0}".format(tag_url)
            elif len(tag_url) > 0 and tag_url[0] == '/':
                return "{0}{1}".format(url_base,  tag_url)
            else:
                return "{0}{1}/{2}".format(url_base,  uri_path,  tag_url)
        return tag_url

    def normalize(self):
        tree = lxml.html.fromstring(self.html)
        # drop noscript tags
        noscript = tree.xpath("//noscript | // NOSCRIPT")
        for ns in noscript:
            ns.drop_tree()
        tree.make_links_absolute(self.url, True)

        bases = tree.xpath("//base | //BASE")
        for b in bases:
            href = b.get('href')
            if href is not None:
                base_url = href

        imgs = tree.xpath("//img | //IMG")
        for img in imgs:
            src = img.get('src')
            if src is not None:
                img.set('src', self.fix_relative_url(self.base_url or self.url, src))

        self.dom_tree = tree
        try:
            self.html = lxml.html.tostring(self.dom_tree)
        except lxml.etree.SerialisationError:
            # Failover case to use utf8 as encoding.
            self.html = lxml.html.tostring(self.dom_tree, encoding='utf8')

        return (self.dom_tree, self.html)

    def extract(self):
        result = {}

        if (self.dom_tree is None):
            self.normalize()

        result['url'] = self.url
        result['type'] = 'website'
        result['images'] = []
        result['title'] = ''
        
        og = opengraph.OpenGraph()
        og.parser(self.html)

        # opengraph parsing
        if 'description' in og:
            result['description'] = og['description']
        if 'title' in og:
            result['title'] = og['title'].strip()
        #if 'url' in og:
        #    result['url'] = og['url']   
        if 'provider_name' in og:
            result['site_name'] = og['site_name']
        if 'video' in og:
            result['videos'] = []

            video = {}
            video['url'] = og['video']
            if 'video:height' in og:
                video['height'] = og['video:height']
            if 'video:width' in og:
                video['width'] = og['video:width']

            result['videos'].append(video)
        if 'type' in og:
            result['type'] = og['type']
        if 'image' in og:
            img = {}
            img['url'] = self.fix_relative_url(self.base_url or self.url, og['image']) 
            if 'image:height' in og:
                img['height'] = og['image:height']
            if 'image:width' in og:
                img['width'] = og['image:width']
            result['images'].append(img)

        p = urlparse(result['url'])
        if p:
            result['provider_display'] = p.netloc.lower()
        else:
            result['provider_display'] = result['url']
                
        if result['title'] == '':
            tags = self.dom_tree.xpath('//title | //TITLE')
            for t in tags:
                result['title'] = t.text.strip()
                break

        # FIXME: this is a workaround to fill-in empty title with URL
        if result['title'] == '':
            result['title'] = self.url

        tags = self.dom_tree.xpath('//meta | //META')
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

        imgs = self.dom_tree.xpath("//img | //IMG")
        for img in imgs:
            width = img.get('width')
            height = img.get('height')
            if width is None and height is None:
                continue
            try:
                if width is not None: 
                    width = int(filter(lambda x:x.isdigit(), width))
                    if width < 100:
                        continue
                if height is not None:
                    height = int(filter(lambda x:x.isdigit(), height))
                    if height < 100:
                        continue
            except:
                continue
            src = img.get('src')
            if src is not None:
                tmp = {'url': self.fix_relative_url(self.base_url or result['url'], src)}
                if tmp not in result['images']:
                    result['images'].append(tmp)

        links = self.dom_tree.xpath("//link | //LINK")
        for l in links:
            rel = l.get('rel')
            if rel is None:
                continue
            rel = rel.lower()
            if rel == 'shortcut icon':
                href = l.get('href')
                if href is not None:
                    result['favicon_url'] = self.fix_relative_url(self.base_url or result['url'], href)
            elif rel == 'image_src':
                href = l.get('href')
                if href is not None:
                    img = {'url': self.fix_relative_url(self.base_url or result['url'], href)}
                    if img not in result['images']:
                        result['images'].append(img)

        return result

    def extractV2(self):
        result = {}

        if (self.dom_tree is None):
            self.normalize()

        result['url'] = self.url
        result['type'] = 'website'
        result['images'] = []
        result['title'] = ''
        
        og = opengraph.OpenGraph()
        og.parser(self.html)

        # opengraph parsing
        if 'title' in og:
            result['title'] = og['title'].strip()
        if 'type' in og:
            result['type'] = og['type']
        if 'image' in og:
            img = {}
            img['url'] = self.fix_relative_url(self.base_url or self.url, og['image']) 
            #if 'image:height' in og:
            #    img['height'] = og['image:height']
            #if 'image:width' in og:
            #    img['width'] = og['image:width']
            result['images'].append(img)

        if result['title'] == '':
            tags = self.dom_tree.xpath('//title | //TITLE')
            for t in tags:
                result['title'] = t.text.strip()
                break

        # FIXME: this is a workaround to fill-in empty title with URL
        if result['title'] == '':
            result['title'] = self.url

        imgs = self.dom_tree.xpath("//img | //IMG")
        for img in imgs:
            # Comment images size checking, remove it if need further
            """
            width = img.get('width')
            height = img.get('height')
            if width is None and height is None:
                continue
            try:
                if width is not None: 
                    width = int(filter(lambda x:x.isdigit(), width))
                    if width < 100:
                        continue
                if height is not None:
                    height = int(filter(lambda x:x.isdigit(), height))
                    if height < 100:
                        continue
            except:
                continue
            """
            src = img.get('src')
            if src is not None:
                tmp = {'url': self.fix_relative_url(self.base_url or result['url'], src)}
                if tmp not in result['images']:
                    result['images'].append(tmp)

        links = self.dom_tree.xpath("//link | //LINK")
        for l in links:
            rel = l.get('rel')
            if rel is None:
                continue
            rel = rel.lower()
            if rel == 'image_src':
                href = l.get('href')
                if href is not None:
                    img = {'url': self.fix_relative_url(self.base_url or result['url'], href)}
                    if img not in result['images']:
                        result['images'].append(img)

        return result
