from readable import *
import lxml.html
import lxml.etree
import re
class BigPicture(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, dom_tree=None, url=None):
        def replace_links(url):
            regex = '//.+'
            if re.match(regex, url):
                return 'http:' + url

        result = {};
    
        rb = Readable()
        readability = rb.grab_article(html)

        if dom_tree is None:
            dom_tree = lxml.html.fromstring(html)

        images = dom_tree.find_class('bpImage')
        result['images'] = []
        captions = dom_tree.find_class('bpCaption')

        text = lxml.html.tostring(readability, pretty_print=True)
        idx = 0
        for img in images:
            text = text + '<p>'
            result['images'].append({'url': img.get('src')})
            text = text + lxml.etree.tostring(img)
            text = text + '\n'
            if captions[idx] != None:
                text = text + lxml.etree.tostring(captions[idx])
                text = text + '\n'
            text = text + '</p>'
            idx = idx + 1

        result['text'] = text
        return result
