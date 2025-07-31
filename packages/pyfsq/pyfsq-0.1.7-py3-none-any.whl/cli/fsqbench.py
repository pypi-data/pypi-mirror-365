#!/usr/bin/env python3

"""FSQ benchmark tool."""

import logging
import argparse
import os
import threading
import time
from typing import List
from fsq.api import FSQ_PROTOCOL_VERSION
from fsq.api import Api as FsqApi
from fsq.misc import DEST_CHOICES, generate_random_str

def perform_task(i: int, timers: List[float], parser_args: argparse.Namespace) -> None:
    """Task to execute by each thread."""
    fsq = FsqApi()
    fsq.connect(node=parser_args.node, password=parser_args.password,
                hostname=parser_args.servername, port=7625)

    random_data = os.urandom(parser_args.size)
    timer_start = time.perf_counter()

    for _ in range(parser_args.number):
        fpath = os.path.join(parser_args.fpath, '', generate_random_str())
        fsq.open(fs=parser_args.fsname, fpath=fpath,
                 desc='', dest=DEST_CHOICES[parser_args.storagedest])
        fsq.write(random_data, parser_args.size)
        fsq.close()

    timers[i] = time.perf_counter() - timer_start

    fsq.disconnect()

def main():
    """The main entry point of the application."""
    parser = argparse.ArgumentParser(description=f'FSQ client for sending files '
                                     f'via FSQ protocol version {FSQ_PROTOCOL_VERSION}')
    parser.add_argument('-z', '--size', type=int, default=16777216,
                        help='[default: 16777216 bytes]')
    parser.add_argument('-b', '--number', type=int, default=16, help='[default: 16]')
    parser.add_argument('-t', '--threads', type=int, default=1, help='[default: 1]')
    parser.add_argument('-f', '--fsname', type=str, default='/lustre',
                        help='[default: /lustre]')
    parser.add_argument('-a', '--fpath', type=str, default='/lustre/fsqbench',
                        help='[default: /lustre/fsqbench]')
    parser.add_argument('-o', '--storagedest', type=str, choices=DEST_CHOICES,
                        default='null', help='storage destination [default: null]')
    parser.add_argument('-n', '--node', type=str, required=True, help='TSM node name')
    parser.add_argument('-p', '--password', type=str, required=True, help='TSM password')
    parser.add_argument('-s', '--servername', type=str, required=True, help='FSQ hostname')
    parser.add_argument('-v', '--verbose', type=str, choices=['critical', 'error',
                                                              'warning', 'info', 'debug'],
                        default='info', help='verbose level [default: info]')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.verbose.upper(), logging.INFO),
                        format='[%(asctime)s %(filename)s:%(lineno)d %(levelname)s] %(message)s')

    results = [None] * args.threads
    threads = []
    for t in range(args.threads):
        thread = threading.Thread(target=perform_task, args=(t, results, args))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    size = args.number * args.size
    for thread, result in zip(threads, results):
        print(f'{thread.name} transmitted {size} bytes in {result:0.4f} secs')

    size_total = size * args.threads
    time_total = sum(results)
    print(f'total transmitted {size_total} bytes in {time_total:0.4f} '
          f'secs ({size_total / 1e9 / time_total:0.4f} Gbytes/secs)')

if __name__ == "__main__":
    main()
