#!/usr/bin/env python

import argparse
import logging
import sys

log = logging.getLogger('katipo')

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('seeds', nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    for s in args.seeds:
        log.debug('seed %s' % (s,))


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s')
    main()
