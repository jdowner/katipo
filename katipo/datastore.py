import hashlib
import logging
import time
import urlparse

import redis

log = logging.getLogger(__name__)

class Datastore(object):
    def __init__(self, pool=None):
        self._redis = redis.Redis(connection_pool=pool)

    def add_to_searched(self, url):
        log.debug('searched %s' % (url,))
        self._redis.sadd('searched', url)

    def add_result(self, url, score):
        self._redis.set('score:%s' % (url,), score)

    def is_searched(self, url):
        return self._redis.sismember('searched', url)

    def pop_pending(self):
        return self._redis.spop('pending')

    def push_pending(self, url):
        log.debug('enqueue %s' % (url,))
        self._redis.sadd('pending', url)

    def mark_as_processing(self, url):
        netloc = urlparse.urlparse(url).netloc
        key = 'processing:%s' % netloc
        if not self._redis.setnx(key, True):
            return False
        self._redis.expire(key, 1)
        return True
