import re
import youtube
import vimeo
import generic_web
import boston_big_pictures
import techcrunch
import ted
import slashdot
import bbc_news
import wikipedia

Verbose=False

class Sites(object):
    SITE_MAP = [
        {
            'regex': '((http|https)://)?www\.youtube\.com(/)?.*',
            'handler': youtube.YouTube(verbose=Verbose)
        },

        {
            'regex': '((http|https)://)?(www\.)?vimeo\.com(/)?.*',
            'handler': vimeo.Vimeo(verbose=Verbose)
        },

        {
            'regex': '((http|https)://)?[a-zA-Z]+.wikipedia.org(/)?.*',
            'handler': wikipedia.Wikipedia(verbose=Verbose)
        },

        {
            'regex': '((http|https)://)?www\.boston\.com/bigpicture/.*',
            'handler': boston_big_pictures.BigPicture(verbose=Verbose)
        },

        {
            'regex': '((http|https)://)?.+slashdot\.org/.*',
            'handler': slashdot.Slashdot(verbose=Verbose)
        },

        {
            'regex': '((http|https)://)?techcrunch\.com/.*',
            'handler': techcrunch.Techcrunch(verbose=Verbose)
        },

        {
            'regex': '((http|https)://)?www\.ted\.com/.*',
            'handler': ted.TedTV(verbose=Verbose)
        },

        {
            'regex': '((http|https)://)?www\.bbc\.co\.uk/.*',
            'handler': bbc_news.BBCNews(verbose=Verbose)
        },

        {
            'regex': '((http|https)://)?www\.bbc\.com/.*',
            'handler': bbc_news.BBCNews(verbose=Verbose)
        },
        
        {
            'regex': '.+',
            'handler': generic_web.GenericWeb(verbose=Verbose)
        }
    ]

    def __init__(self, url):
        self.url = url
        self.site_handler = False
        for site in self.SITE_MAP:
            if re.match(site['regex'], url):
                self.site_handler = site['handler']
                break

    def is_match(self):
        return self.site_handler

    def parse(self, html, dom_tree=None):
        return self.site_handler.run(html, dom_tree=dom_tree, url=self.url)


