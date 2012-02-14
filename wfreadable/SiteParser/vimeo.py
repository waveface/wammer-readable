import lxml.html
from readable import *
import opengraph
class Vimeo(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, url=None):
        rb = Readable()
        tree = rb.grab_article(html)
        desc = lxml.html.tostring(tree, pretty_print=True)

        og = opengraph.OpenGraph()
        metas = og.parser(html)
        if og.is_valid():
            if self.verbose:
                for x,y in og.items():
                    print "%-15s => %s" % (x, y)
        
            result = desc
            #if 'title' in og:
            #    result += "<h1>%s</h1>" % og['title']
            #if 'description' in og:
            #    result += '<p>%s</p>\n' % og['description'] 

            if 'video' in og:
                height = 640
                if 'video:height' in og:
                     height = og['video:height']
                width = 391
                if 'video:width' in og:
                    width = og['video:width']
                result += '<p><iframe src="{0}" frameborder="0" width="{1}" height="{2}"></embed></p>'.format(og['video'], width, height)
                result += '<br/>\n'
            return result
            
        else:
            return desc
