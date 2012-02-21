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
                if 'video:height' in og:
                    video['height'] = og['video:height']
                    h = video['height']
                w = 640
                if 'video:width' in og:
                    video['width'] = og['video:width']
                    w = video['width']
                video['url'] = og['video']
                result['videos'].append(video)

                #embed = '<p><embed id="yt" src="{0}" type="application/x-shockwave-flash" width="{1}" height="{2}"></embed></p>'.format(og['video'], w, h)
                paths = urlparse.urlparse(video['url']).path.split('/')
                src = "http://www.youtube.com/embed/{0}".format(paths[2])
                embed = '<p><iframe type="text/html" width="{0}" height="{1}" src="{2}" frameborder="0"></iframe></p'.format(w, h, src)
                result['content'] = "{0}{1}".format(embed, desc)
        return result
            
