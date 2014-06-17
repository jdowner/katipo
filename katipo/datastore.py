import hashlib
import logging

import redis

log = logging.getLogger(__name__)

class Datastore(object):
    def __init__(self, corpus, pool=None):
        chash = hashlib.md5()
        for c in corpus:
            chash.update(c)

        self._corpus_id = chash.hexdigest()
        self._redis = redis.Redis(connection_pool=pool)

        self._prefix = {term: '%s:%s' % (self._corpus_id, term) for term in
                ('corpus','searched', 'pending', 'scored')}

        self._redis.sadd(self.prefix['corpus'], corpus)

    @property
    def prefix(self):
        return self._prefix

    @property
    def corpus_id(self):
        return self._corpus_id

    def corpus(self):
        return self._redis.smembers(self.prefix['corpus'])

    def add_to_searched(self, url):
        log.debug('searched %s' % (url,))
        self._redis.sadd(self.prefix['searched'], url)

    def add_result(self, url, score):
        self._redis.hmset(self.prefix['scored'], {'url': url, 'score':score})

    def pending(self):
        return self._redis.smembers(self.prefix['pending'])

    def searched(self):
        return self._redis.smembers(self.prefix['searched'])

    def is_searched(self, url):
        return self._redis.sismember(self.prefix['searched'], url)

    def pop_pending(self):
        return self._redis.spop(self.prefix['pending'])

    def push_pending(self, url):
        log.debug('enqueue %s' % (url,))
        self._redis.sadd(self.prefix['pending'], url)
