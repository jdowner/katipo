#!/usr/bin/env python

import argparse
import logging
import sys

import zmq.eventloop.ioloop

log = logging.getLogger('katipo')

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('seeds', nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    for s in args.seeds:
        log.debug('seed %s' % (s,))

    try:
        log.info('katipo started')
        loop = zmq.eventloop.ioloop.IOLoop.instance()
        loop.start()
    except Exception as e:
        log.exception(e)
    except KeyboardInterrupt, SystemExit:
        log.info('exiting due to interrupt')
    finally:
        log.info('katipo stoppped')


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s')
    main()
