from readable import *
import lxml.html
import os 
import urlparse
import re

class BBCNews(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def run(self, html, dom_tree=None, url=None):
        result = {}

        tree = dom_tree.get_element_by_id("main-content")
        if tree is None:
            rb = Readable()
            tree = rb.grab_article(html)
            if tree is not None:
                result['score'] = tree.readable.score
        else:
            opts = dict(scripts=True, javascript=True, comments=True,
                        style=True, links=True, meta=False, page_structure=False,
                        processing_instructions=True, embedded=False, frames=False,
                        forms=False, annoying_tags=False, safe_attrs_only=False)
            cleaner = lxml.html.clean.Cleaner(**opts)
            cleaner(tree)
            headers = tree.find_class("story-header")
            for hd in headers:
                hd.drop_tree()
            try:
                most_watch = tree.get_element_by_id("most-watched")
                if most_watch is not None:
                    most_watch.drop_tree()
            except Exception:
                pass

            try:
                bookmark_header = tree.get_element_by_id("page-bookmark-links-head")
                if bookmark_header is not None:
                    bookmark_header.drop_tree()
                bookmark_footer = tree.get_element_by_id("page-bookmark-links-foot")
                if bookmark_footer is not None:
                    bookmark_footer.drop_tree()
            except Exception:
                pass

            hyperpuff = tree.find_class("hyperpuff")
            for hp in hyperpuff:
                hp.drop_tree()

        if tree is not None:
            result['content'] = lxml.html.tostring(tree, pretty_print=True)

            tree = lxml.html.fromstring(result['content'])
            result['images'] = []
            imgs = tree.xpath('//img | //IMG')
            for img in imgs:
                src = img.get('src')
                if src is not None:
                    result['images'].append({'url': src})

            return result
        else:
            return None
