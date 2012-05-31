from readable import *
import lxml.html
import os 
import urlparse
import re

def fix_src(url, html_tree, url_base=None):
    uri_path = ""
    if url_base is None:
        urlparts = urlparse.urlparse(url)
        if (urlparts.scheme == ''):
            url_base = 'http://' + urlparts.netloc 
        else:
            url_base = urlparts.scheme + '://' + urlparts.netloc

        uri_path = os.path.dirname(urlparts.path)

    regex = "(http|https|ftp)://.*"
    pattern = re.compile(regex)

    imgs = html_tree.xpath("//img")
    for img in imgs: 
        src = img.get("src")
        if src is not None and not pattern.match(src):
            if src[0] == '/':
                img.set("src", "{0}{1}".format(url_base, src))
            else:
                img.set("src", "{0}{1}{2}".format(url_base, uri_path, src))

    atags = html_tree.xpath("//a")
    for atag in atags:
        href = atag.get("href")
        if href is not None and not pattern.match(href):
            if href[0] == '/':
                atag.set("href", "{0}{1}".format(url_base, href))
            else:
                atag.set("href", "{0}{1}{2}".format(url_base, uri_path, href))


class GenericWeb(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, dom_tree=None, url=None):
        result = {}

        rb = Readable()
        tree = rb.grab_article(html)

        if tree is not None:
            # this is unique in slashdot 
            tree = tree.get_element_by_id('firehoselist')
            result['content'] = lxml.html.tostring(tree, pretty_print=True)

            tree = lxml.html.fromstring(result['content'])
            result['images'] = []
            imgs = tree.xpath('//img | //IMG')
            for img in imgs:
                src = img.get('src')
                if src is not None:
                    result['images'].append({'url': src})

            return result
        else:
            return None
