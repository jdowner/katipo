#!/usr/bin/env python3

import argparse
import concurrent.futures as cf
import logging
import sys

import katipo

log = logging.getLogger('katipo')

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-w', '--workers', type=int)
    parser.add_argument('-c', '--corpus')
    parser.add_argument('seeds', nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)

    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    try:
        with open(args.corpus) as fd:
            corpus = {line.strip() for line in fd if line}

        log.info('katipo started')

        datastore = katipo.Datastore()
        for seed in args.seeds:
            datastore.push_pending(seed)

        futures = []
        with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
            while True:
                while len(futures) < args.workers:
                    traverse = katipo.Traverse(corpus)
                    futures.append(executor.submit(traverse))

                cf.wait(futures, return_when=cf.FIRST_COMPLETED)
                futures = [f for f in futures if f.running()]


    except Exception as e:
        log.exception(e)
    except (KeyboardInterrupt, SystemExit):
        log.info('exiting due to interrupt')
    finally:
        log.info('katipo stoppped')


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s')
    main()
