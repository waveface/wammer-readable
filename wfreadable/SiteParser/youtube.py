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
                h = 640
                if 'video:height' in og:
                    video['height'] = og['video:height']
                    h = video['height']
                w = 391
                if 'video:width' in og:
                    video['width'] = og['video:width']
                    w = video['width']
                video['url'] = og['video']
                result['videos'].append(video)

                embed = '<p><embed id="yt" src="{0}" type="application/x-shockwave-flash" width="{1}" height="{2}"></embed></p>'.format(og['video'], h, w)
                result['content'] = "{0}{1}".format(embed, desc)
            return result
            
        else:
            return desc
