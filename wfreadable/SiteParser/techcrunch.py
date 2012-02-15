from readable import *
import lxml.html
import re
class Techcrunch(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, dom_tree=None, url=None):
        result = {}
        rb = Readable()
        tree = rb.grab_article(html)
        authors = tree.find_class('author-dropdown')
        for a in authors:
            a.drop_tree()

        result['text'] = lxml.html.tostring(tree, pretty_print=True)

        result['images'] = []
        images = tree.xpath('//img | //IMG')
        for img in images:
            result['images'].append({'url': img.get('src')})

        return result
