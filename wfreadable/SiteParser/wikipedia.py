from readable import *
import lxml.html
import os 
import urlparse
import re

class Wikipedia(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, dom_tree=None, url=None):
        result = {}

        rb = Readable()
        tree = rb.grab_article(html)

        try:
            toc = tree.get_element_by_id('toc')
            if toc is not None:
                toc.drop_tree()
        except Exception:
            pass

        es_spans = tree.find_class("editsection")
        for sp in es_spans:
            sp.drop_tree()


        if tree is not None:
            result['content'] = lxml.html.tostring(tree, pretty_print=True)
            result['score'] = tree.readable.score

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
