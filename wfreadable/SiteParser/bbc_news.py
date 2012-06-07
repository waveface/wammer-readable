from readable import *
import lxml.html
import os 
import urlparse
import re

class BBCNews(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, dom_tree=None, url=None):
        result = {}

        tree = dom_tree.get_element_by_id("main-content")
        if tree is None:
            rb = Readable()
            tree = rb.grab_article(html)
            if tree is not None:
                result['score'] = tree.readable.score

        if tree is not None:
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
