import lxml.html
from readable import *
import opengraph
class YouTube(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, dom_tree=None, url=None):
        result = {}
        rb = Readable()
        tree = rb.grab_article(html)
        desc = lxml.html.tostring(tree, pretty_print=True)

        og = opengraph.OpenGraph()
        metas = og.parser(html)
        if og.is_valid():
            if self.verbose:
                for x,y in og.items():
                    print "%-15s => %s" % (x, y)
        
            result['content'] = desc
            result['videos'] = []

            if 'video' in og:
                video = {}
                if 'video:height' in og:
                    video['height'] = og['video:height']
                if 'video:width' in og:
                    video['width'] = og['video:width']
                video['url'] = og['video']
                result['videos'].append(video)
            return result
            
        else:
            return desc
