import hashlib
import logging
import urlparse
import string

from bs4 import BeautifulSoup
import nltk
import requests
import tornado.gen

import datastore

log = logging.getLogger(__name__)

class Traverse(object):
    """
    A Traverse object takes a corpus and a set of seed URLs and performs a
    traversal of the links to URLs contained within. Because the URLs that are
    discovered are placed in a set, the order that they are discovered in is not
    preserved. Thus the traversal is neither a depth-first nor a breadth-first
    traversal.
    """

    def __init__(self, seeds, corpus):
        """
        Creates a Traversal object.

        """
        self._corpus = corpus
        self._datastore = datastore.Datastore(corpus)

        for s in seeds:
            self._datastore.push_pending(s)

    @property
    def corpus(self):
        return self._corpus

    def should_search(self, url):
        headers = requests.head(url).headers
        return headers.get('content-type', '').startswith('text/html')

    @tornado.gen.coroutine
    def run(self):
        try:
            # remove the url from the queue and add it to the 'searched' set so
            # that it is never search again.
            url = self._datastore.pop_pending()
            if url is None:
                return

            self._datastore.add_to_searched(url)

            if not self.should_search(url):
                return

            text = requests.get(url).text
            soup = BeautifulSoup(text)

            # calculate a hash for the text
            uhash = hashlib.md5(text.encode('utf-8')).hexdigest()

            # determine the score for the text
            score = self.score(text)
            self._datastore.add_result(url, score)
            log.info('score %d %s' % (score, url))

            for a in soup.find_all('a', href=True):
                link = a['href']

                # convert relative URLs into absolute URLs
                if not link.startswith('http'):
                    link = urlparse.urljoin(url, link)

                # if the join does not work, ignore this URL
                if not link.startswith('http'):
                    continue

                # if link is already searched, skip it
                if self._datastore.is_searched(link):
                    continue

                # add link to pending searches
                self._datastore.push_pending(link)
        except Exception as e:
            log.exception(e)

    def score(self, text):
        tokens = nltk.word_tokenize(text.lower())
        tokens = {t for t in tokens if t not in string.punctuation}
        return len(tokens.intersection(self.corpus))
