import sys
import os
import urllib
import SiteParser
import re
from urllib import URLopener
from urllib import FancyURLopener
from WebParser import *

class WFReadable(object):
    def __init__(self, url, html=None):
        if (re.match("http(s)?://.+", url)) is None:
            url = "http://{0}".format(url)

        if not html:
            self.html = self.fetch_page(url)
        else:
            self.html = html
        self.url = url

    def fetch_page(self, url):
        class MyOpener(FancyURLopener):
            version = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_7) AppleWebKit/534.27+ (KHTML, like Gecko) Version/5.0.4 Safari/533.20.2"
        myopener = MyOpener()
        page = myopener.open(url)
        if page.getcode() == 200:
            content = page.read()
            charset = page.headers.getparam('charset')
            if charset is None:
                import BeautifulSoup
                soup = BeautifulSoup.BeautifulSoup(content)
                charset = soup.originalEncoding
            try:
                return content.decode(charset)
            except UnicodeDecodeError:
                return content
        else:
            return ''

    def summarize(self, text, wordno):
        try:
            utext = unicode(text, 'utf-8')
        except TypeError:
            utext = text
        textlen = len(utext)
        if textlen < wordno:
            return text

        final = []
        words = text.split(" ")
        wc = 0
        for w in words:
            l = len(w)
            if l > 12:
                if wc + l > wordno:
                    remaining = wordno-wc
                    final.append(w[:remaining])
                    break
                else:
                    final.append(w)
                    wc += len(w)
            else:
                wc += 1
                final.append(w)
            if wc > wordno:
                break
        return " ".join(final) + "..."

    def parse(self):
        wp = WebParser(self.html, self.url)
        result = wp.parse()

        site = SiteParser.Sites(self.url)
        text = None
        if site.is_match():
            soul = site.parse(self.html)
            soul = re.sub(r'\s+', ' ', soul)
            result['text'] = soul

            soul_tree = lxml.html.fromstring(soul)
            soul_text_only = soul_tree.text_content()
            s = self.summarize(soul_text_only, 50)
            if 'description' not in result:
                result['description'] = s
        return result

