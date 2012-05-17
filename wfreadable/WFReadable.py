import sys
import os
import urllib2
import cookielib
import SiteParser
import re
from WebParser import *
import traceback

class PageFetchError(Exception):
    def __init__(self, trace=None):
        self.traceback = trace

    def __str__(self):
        return "", "Fail to fetch the web page"

class WebParseError(Exception):
    def __init__(self, trace=None):
        self.traceback = trace

    def __str__(self):
        return "", "Fail to parse web page"

class WebSummarizeError(Exception):
    def __init__(self, trace=None):
        self.traceback = trace

    def __str__(self):
        return "", "Fail to summarize web page"

class ImagePageURL(Exception):
    def __init__(self, trace=None):
        self.traceback = trace

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

    def url_preprocessing(self, url):
        if (re.match(".*blogspot.com.*", url, flags=re.IGNORECASE)) or (re.match(".*blogger.com.*", url, flags=re.IGNORECASE)) or (re.match(".*examiner.com.*", url, flags=re.IGNORECASE)):
            if url.find('m=1') < 0:
                return unicode("{0}?m=1".format(url))
        return unicode(url)

    def fetch_page(self, url):
        jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
   #     opener.addheaders = [('User-agent', "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3")]
        url = self.url_preprocessing(url)
        request = urllib2.Request(url.encode('utf-8'))
        
        page = opener.open(request)
        if page.getcode() == 200:
            text = False
            result = {}
            result['type'] = 'html'

            # fix the url if we are redirected
            self.url = page.geturl()

            ctype = page.headers['content-type']
            if re.match("image/.+", ctype, flags=re.I):
                result['type'] = 'image'
                result['content'] = '<img src="{0}"/>'.format(url)
                return result

            if re.match("text/plain", ctype, flags=re.I):
                result['type'] = 'text'
                text = True
            content = page.read()
            charset = None
            if 'charset' in page.headers:
                charset = page.headers['charset']
            if text is False and charset is None:
                import BeautifulSoup
                soup = BeautifulSoup.BeautifulSoup(content)
                charset = soup.originalEncoding
            try:
                if charset is None:
                    result['content'] = content
                else:
                    result['content'] = content.decode(charset)
            except UnicodeDecodeError:
                result['content'] = content
            return result
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
            if w == '': 
                continue
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
                dw = self.fetch_page(self.url)
                self.html = dw['content']
                if self.html == None:
                    return None

                if dw['type'] == 'image':
                    result = {}
                    result['content'] = '<img src="{0}"/>'.format(self.url)
                    return result

                if dw['type'] == 'text':
                    result = {}
                    result['content'] = dw['content']
                    return result

            except IOError:
                raise PageFetchError

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
                s = self.summarize(soul_text_only, 75)
                result['description'] = s

                return result
            return None
        except Exception, e:
            stack = traceback.format_stack(sys.exc_info()[2].tb_frame)
            ss = "".join(stack)
            tb = traceback.format_tb(sys.exc_info()[2])
            stb = "".join(tb)
            raise WebSummarizeError("{0}\n{1}\n{2}".format(stb, ss, e))
 

    def parse(self):
        if self.html is None:
            try:
                dw = self.fetch_page(self.url)
                self.html = dw['content']
                if self.html == None:
                    return None

                if dw['type'] == 'image':
                    result = {}
                    result['images'] = []
                    result['images'].append({'url': self.url})
                    p = urlparse(self.url)
                    if 'netloc' in p:
                        result['provider_display'] = p.netloc.lower()
                    else:
                        result['provider_display'] = ''
                    result['url'] = self.url
                    result['type'] = 'image'
                    result['description'] = ''
                    result['content'] = dw['content']
                    result['title'] = ''
                    return result

                if dw['type'] == 'text':
                    result = {}
                    result['images'] = []
                    result['url'] = self.url
                    result['type'] = 'article'
                    content = dw['content'].strip()
                    result['description'] = self.summarize(content, 75)
                    result['content'] = content
                    result['title'] = self.summarize(content, 10)
                    return result
                    
            except IOError:
                raise PageFetchError

        result = {}
        try:
            wp = WebParser(self.html, self.url)
            (self.dom_tree, self.html) = wp.normalize()
            result = wp.extract()
        except Exception, e:
            stack = traceback.format_stack(sys.exc_info()[2].tb_frame)
            ss = "".join(stack)
            tb = traceback.format_tb(sys.exc_info()[2])
            stb = "".join(tb)
            raise WebParseError("{0}\n{1}\n{2}".format(stb, ss, e))

        t = self.extract_content()
        if t is not None:
            result['content'] = t['content']
            if 'description' not in result:
                result['description'] = t['description']
            elif 'score' in t and t['score'] > 10:  #if our extraction got higher score
                result['description'] = t['description']

            if 'images' in t:
                result['images'] = self.merge_url_array(result['images'], t['images'])

        return result

