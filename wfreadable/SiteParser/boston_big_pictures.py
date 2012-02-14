from readable import *
import lxml.html
import lxml.etree
import re
class BigPicture(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, url=None):
        def replace_links(url):
            regex = '//.+'
            if re.match(regex, url):
                return 'http:' + url
        rb = Readable()
        readability = rb.grab_article(html)

        content = lxml.html.fromstring(html)
        images = content.find_class('bpImage')
        captions = content.find_class('bpCaption')

        result = lxml.html.tostring(readability, pretty_print=True)
        idx = 0
        for img in images:
            result = result + '<p>'
            result = result + lxml.etree.tostring(img)
            result = result + '\n'
            if captions[idx] != None:
                result = result + lxml.etree.tostring(captions[idx])
                result = result + '\n'
            result = result + '</p>'
            idx = idx + 1

        return result
