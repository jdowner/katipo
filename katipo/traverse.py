import hashlib
import logging
import urlparse
import string

from bs4 import BeautifulSoup
import nltk
import requests

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

    def __init__(self, corpus):
        """
        Creates a Traversal object.

        """
        self._corpus = corpus

    @property
    def corpus(self):
        return self._corpus

    def should_search(self, url):
        headers = requests.head(url).headers
        return headers.get('content-type', '').startswith('text/html')

    def __call__(self):
        try:
            db = datastore.Datastore()

            # remove the url from the queue and add it to the 'searched' set so
            # that it is never searched again.
            url = db.pop_pending()
            if url is None:
                return

            # Tag the URL as being processed. If it cannot be tagged as
            # processed that means that it is being processed by another process
            # or thread, which means we should not process it here.
            if not db.mark_as_processing(url):
                log.debug('already processing %s' % url)
                db.push_pending(url)
                return

            db.add_to_searched(url)

            if not self.should_search(url):
                return

            text = requests.get(url).text
            soup = BeautifulSoup(text)

            # calculate a hash for the text
            uhash = hashlib.md5(text.encode('utf-8')).hexdigest()

            # determine the score for the text
            score = self.score(text)
            db.add_result(url, score)
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
                if db.is_searched(link):
                    continue

                # add link to pending searches
                db.push_pending(link)
        except Exception as e:
            log.exception(e)

    def score(self, text):
        tokens = nltk.word_tokenize(text.lower())
        tokens = {t for t in tokens if t not in string.punctuation}
        return len(tokens.intersection(self.corpus))
