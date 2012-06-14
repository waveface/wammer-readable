import lxml.html
from readable import *
import opengraph
from urlparse import urlparse
class Vimeo(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def _findMetaContentByXpath(self, tree, path):
        items = tree.xpath(path)
        if items is None:
            return None

        for item in items:
            return item.get('content')

        return None

    def run(self, html, dom_tree, url=None):
        result = {}

        desc = None
        try:
            desc_tag = dom_tree.get_element_by_id('description')
            if desc_tag is not None:
                desc = lxml.html.tostring(desc_tag)
        except KeyError:
            pass

        if desc is None:
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

                if 'url' in og:
                    p = urlparse(og['url'])
                else:
                    p = urlparse(url)
                if p is not None:
                    player = "http://player.vimeo.com/video{0}".format(p.path)
                else:
                    player = og['video']

                result['videos'].append(video)
                embed = '<p><iframe src="{0}" frameborder="0" width="{1}" height="{2}" webkitAllowFullScreen mozallowfulllscreen allowFullScreen></iframe></p>'.format(player, w, h)
                result['content'] = '{0}{1}'.format(embed, desc)

        else: # there is no og tag, since someday, vimeo didn't support opengraph tags
            video = {}
            embedUrl = self._findMetaContentByXpath(dom_tree, "//meta[@itemprop='embedUrl']")
            if embedUrl is None:
                return result
            video['url'] = embedUrl
            height = self._findMetaContentByXpath(dom_tree, "//meta[@itemprop='height']")
            if height is not None:
                video['height'] = height
            else:
                height = 391
            width = self._findMetaContentByXpath(dom_tree, "//meta[@itemprop='width']")
            if width is not None:
                video['width'] = width
            else:
                width = 640

            thumb = self._findMetaContentByXpath(dom_tree, "//meta[@itemprop='image']")
            if thumb is not None:
                image = {}
                image['url'] = thumb
                image['height'] = height
                image['width'] = width
                if 'images' not in result:
                    result['images'] = []
                result['images'].append(image)

            result['videos'] = []
            result['videos'].append(video)
            embed = '<p><iframe src="{0}" frameborder="0" width="{1}" height="{2}" webkitAllowFullScreen mozallowfulllscreen allowFullScreen></iframe></p>'.format(embedUrl, 640, 391)
            result['content'] = '{0}{1}'.format(embed, desc)
                
        return result
            
