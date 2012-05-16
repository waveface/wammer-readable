import lxml.html
from readable import *
import opengraph
import urlparse
class TedTV(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, dom_tree=None, url=None):
        result = {}
        rb = Readable()
        tree = rb.grab_article(html)
        desc = lxml.html.tostring(tree, pretty_print=True)
        result['content'] = desc

        og = opengraph.OpenGraph()
        metas = og.parser(html)
        if og.is_valid():
            if self.verbose:
                for x,y in og.items():
                    print "%-15s => %s" % (x, y)
        
            result['videos'] = []

            if 'video' in og:
                video = {}
                h = 391
                video['url'] = og['video']
                result['videos'].append(video)

                result['content'] = "<video width='350' src='{0}'/></video><br/>{1}".format(video['url'], result['content'])
        return result
            
