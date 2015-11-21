import hashlib
import logging
import time
import urlparse

import redis

log = logging.getLogger(__name__)

class Datastore(object):
    def __init__(self, pool=None):
        self.redis = redis.Redis(connection_pool=pool)

    def add_to_searched(self, url):
        log.debug('searched %s' % (url,))
        self.redis.sadd('searched', url)

    def add_result(self, url, score):
        self.redis.set('score:%s' % (url,), score)

    def is_searched(self, url):
        return self.redis.sismember('searched', url)

    def pop_pending(self):
        return self.redis.spop('pending')

    def push_pending(self, url):
        log.debug('enqueue %s' % (url,))
        self.redis.sadd('pending', url)

    def mark_as_processing(self, url):
        netloc = urlparse.urlparse(url).netloc
        key = 'processing:%s' % netloc
        if not self.redis.setnx(key, True):
            return False
        self.redis.expire(key, 1)
        return True

    def corpus_add_word(self, word):
        self.redis.sadd("corpus", word)

    def corpus_remove_word(self, word):
        self.redis.srem("corpus", word)

    def corpus_list_words(self):
        return list(self.redis.smembers("corpus"))

    def corpus_clear(self):
        words = self.corpus_list_words()
        if words:
            self.redis.srem("corpus", *words)
