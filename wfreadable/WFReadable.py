import sys
import os
import urllib
import SiteParser
import re
from urllib import URLopener
from urllib import FancyURLopener
from WebParser import *

class PageFetchError(Exception):
    pass

class WebParseError(Exception):
    pass

class WebSummarizeError(Exception):
    pass
    

class WFReadable(object):
    def __init__(self, url, html=None):
        if (re.match("http(s)?://.+", url)) is None:
            url = "http://{0}".format(url)

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

    def _summarize(self, text, wordno):
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

    def summarize_content(self):
        if self.html is None:
            try:
                self.html = self.fetch_page(self.url)
            except IOError:
                raise PageFetchError

        try:
            result = {}
            site = SiteParser.Sites(self.url)
            text = None
            if site.is_match():
                soul = site.parse(self.html)
                soul = re.sub(r'\s+', ' ', soul)
                result['text'] = soul

                soul_tree = lxml.html.fromstring(soul)
                soul_text_only = soul_tree.text_content()
                s = self._summarize(soul_text_only, 50)
                result['description'] = s

                return result
            return None
        except:
            raise WebSummarizeError
 

    def parse(self):
        if self.html is None:
            try:
                self.html = self.fetch_page(self.url)
            except IOError:
                raise PageFetchError

        result = {}
        try:
            wp = WebParser(self.html, self.url)
            result = wp.parse()
        except:
            raise WebParseError
            pass

        t = self.summarize_content()
        if t is not None:
            result['text'] = t['text']
            if 'description' not in result:
                result['description'] = t['description']
            elif len(t['description']) > 30:
                result['description'] = t['description']

            # fix the images array
            tree = lxml.html.fromstring(t['text'])
            images = []
            imgs = tree.xpath('//img | //IMG')
            for img in imgs:
                src = img.get('src')
                if src is not None:
                    images.append({'url': src})

            result['images'] = result['images'] + images

        return result

