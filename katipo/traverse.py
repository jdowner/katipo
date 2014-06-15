import logging

import tornado.gen

log = logging.getLogger(__name__)

class Traverse(object):
    def __init__(self, seeds):
        self._pending = set(seeds)

    @property
    def pending(self):
        return self._pending

    @tornado.gen.coroutine
    def run(self):
        if self.pending:
            url = self.pending.pop()
            log.info('searching %s' % (url,))
