#!/usr/bin/env python

import argparse
import logging
import sys

import zmq.eventloop.ioloop

import katipo

log = logging.getLogger('katipo')

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-p', '--period', type=int, default=1000)
    parser.add_argument('-c', '--corpus')
    parser.add_argument('seeds', nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    for s in args.seeds:
        log.debug('seed %s' % (s,))

    try:
        with open(args.corpus) as fd:
            corpus = {line.strip() for line in fd if line}

        log.info('katipo started')
        loop = zmq.eventloop.ioloop.IOLoop.instance()

        traverse = katipo.Traverse(args.seeds, corpus)
        traverse_cb = zmq.eventloop.ioloop.PeriodicCallback(
            traverse.run,
            args.period,
            io_loop=loop)

        traverse_cb.start()
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
