import hashlib
import logging
import urlparse

from bs4 import BeautifulSoup
import requests
import tornado.gen

log = logging.getLogger(__name__)

class Traverse(object):
    def __init__(self, seeds):
        self._searched = []
        self._pending = set(seeds)

    @property
    def pending(self):
        return self._pending

    @property
    def searched(self):
        return self._searched

    @tornado.gen.coroutine
    def run(self):
        try:
            if not self.pending:
                return

            url = self.pending.pop()
            self._searched.append(url)

            headers = requests.head(url).headers
            if not headers.get('content-type', '').startswith('text/html'):
                return

            log.info('searching %s' % (url,))
            text = requests.get(url).text
            soup = BeautifulSoup(text)

            uhash = hashlib.md5(text.encode('utf-8')).hexdigest()
            log.info('hash %s %s' % (url, uhash))

            for a in soup.find_all('a', href=True):
                link = a['href']

                # ignore links in the same page
                if link.startswith('#') or link.startswith('javascript'):
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
