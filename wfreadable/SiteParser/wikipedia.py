from readable import *
import lxml.html
import re
class Wikipedia(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, url=None):
        def replace_links(url):
            regex = '//.+'
            if re.match(regex, url):
                return 'http:' + url

        rb = Readable()
        tree = rb.grab_article(html)
        tree.rewrite_links(replace_links)

        return lxml.html.tostring(tree, pretty_print=True)

