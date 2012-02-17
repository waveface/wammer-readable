import sys
import os
import urllib
import SiteParser
import re
from urllib import URLopener
from urllib import FancyURLopener
from WebParser import *

class PageFetchError(Exception):
    def __init__(self):
        return
    def __str__(self):
        return "", "Fail to fetch the web page"

class WebParseError(Exception):
    def __init__(self):
        return
    def __str__(self):
        return "", "Fail to parse web page"

class WebSummarizeError(Exception):
    def __init__(self):
        return
    def __str__(self):
        return "", "Fail to summarize web page"

class ImagePageURL(Exception):
    def __init__(self):
        return
    def __str__(self):
        return "", "Image page url"
    

class WFReadable(object):
    def __init__(self, url, html=None):
        if (re.match("http(s)?://.+", url, flags=re.IGNORECASE)) is None:
            url = "http://{0}".format(url)

        self.html = html
        self.dom_tree = None
        self.url = url

    def merge_url_array(self, array1, array2):
        resulting_list = list(array1)
        resulting_list.extend (x for x in array2 if x not in resulting_list)
        return resulting_list

    def fetch_page(self, url):
        class MyOpener(FancyURLopener):
            version = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_7) AppleWebKit/534.27+ (KHTML, like Gecko) Version/5.0.4 Safari/533.20.2"
        myopener = MyOpener()
        page = myopener.open(url)
        if page.getcode() == 200:
            ctype = page.headers['content-type']
            if re.match("image/.+", ctype, flags=re.I):
                raise ImagePageURL
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
            return None

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

    def extract_content(self):
        if self.html is None:
            try:
                self.html = self.fetch_page(self.url)
                if self.html == None:
                    return None
            except IOError:
                raise PageFetchError
            except ImagePageURL:
                result = {}
                result['content'] = '<img src="{0}"/>'.format(self.url)
                return result

        if self.dom_tree is None:
            wp = WebParser(self.html, self.url)
            (self.dom_tree, self.html) = wp.normalize()

        try:
            result = {}
            site = SiteParser.Sites(self.url)
            if site.is_match():
                result = site.parse(self.html, self.dom_tree)
                if 'content' in result:
                    # strip continous space
                    result['content'] = re.sub(r'\s+', ' ', result['content'])

                soul_tree = lxml.html.fromstring(result['content'])
                soul_text_only = soul_tree.text_content()
                s = self.summarize(soul_text_only, 50)
                result['description'] = s

                return result
            return None
        except:
            raise WebSummarizeError
 

    def parse(self):
        if self.html is None:
            try:
                self.html = self.fetch_page(self.url)
                if self.html == None:
                    return None
            except IOError:
                raise PageFetchError
            except ImagePageURL:
                result = {}
                result['images'] = []
                result['images'].append({'url': self.url})
                p = urlparse(self.url)
                if 'netloc' in p:
                    result['provider_display'] = p.netloc
                else:
                    result['provider_display'] = ''
                result['url'] = self.url
                result['type'] = 'image'
                result['description'] = ''
                result['content'] = '<img src="{0}"/>'.format(self.url)
                return result

        result = {}
        try:
            wp = WebParser(self.html, self.url)
            (self.dom_tree, self.html) = wp.normalize()
            result = wp.extract()
        except:
            raise WebParseError

        t = self.extract_content()
        if t is not None:
            result['content'] = t['content']
            if 'description' not in result:
                result['description'] = t['description']
            elif 'score' in result and result['score'] > 10:
                result['description'] = t['description']

            if 'images' in t:
                result['images'] = self.merge_url_array(result['images'], t['images'])

        return result

