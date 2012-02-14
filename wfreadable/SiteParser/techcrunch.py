from readable import *
import lxml.html
import re
class Techcrunch(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, url=None):
        rb = Readable()
        tree = rb.grab_article(html)
        authors = tree.find_class('author-dropdown')
        for a in authors:
            a.drop_tree()
        return lxml.html.tostring(tree, pretty_print=True)

