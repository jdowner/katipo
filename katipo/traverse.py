import hashlib
import logging
import urlparse
import string

from bs4 import BeautifulSoup
import nltk
import requests
import tornado.gen

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
        self._searched = set()
        self._pending = set(seeds)
        self._corpus = corpus

    @property
    def pending(self):
        return self._pending

    @property
    def searched(self):
        return self._searched

    @property
    def corpus(self):
        return self._corpus

    def should_ignore(self, link):
        return link.startswith('#') or link.startswith('javascript')

    def should_search(self, url):
        headers = requests.head(url).headers
        return headers.get('content-type', '').startswith('text/html')

    @tornado.gen.coroutine
    def run(self):
        if not self.pending:
            return

        try:
            # remove the url from the queue and add it to the 'searched' set so
            # that it is never search again.
            url = self.pending.pop()
            self._searched.add(url)

            if not self.should_search(url):
                return

            log.info('searching %s' % (url,))
            text = requests.get(url).text
            soup = BeautifulSoup(text)

            # calculate a hash for the text
            uhash = hashlib.md5(text.encode('utf-8')).hexdigest()
            log.info('hash %s %s' % (url, uhash))

            # determine the score for the text
            score = self.score(text)
            log.info('score %s %f' % (url, score))

            for a in soup.find_all('a', href=True):
                link = a['href']

                # ignore links in the same page
                if self.should_ignore(link):
                    continue

                # convert relative URLs into absolute URLs
                if not link.startswith('http'):
                    link = urlparse.urljoin(url, link)

                # if link is already searched, skip it
                if link in self.searched:
                    continue

                # add link to pending searches
                log.debug('enqueue %s' % (link,))
                self._pending.add(link)
        except Exception as e:
            log.exception(e)

    def score(self, text):
        tokens = nltk.word_tokenize(text.lower())
        tokens = {t for t in tokens if t not in string.punctuation}
        return len(tokens.intersection(self.corpus))
