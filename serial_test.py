#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 21:53
# @remark 串口测试入口程序

import sys
import gevent

from libs.argv_parser import ArgvParser
from libs.task_runner import TaskRunner

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python serial_test.py <config_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        config_lines = [l for l in (l.strip() for l in f.readlines()) if l and not l.startswith('#')]

    argv_parser = ArgvParser(config_lines)
    tasks = [TaskRunner(argv_parser.args, port) for port in argv_parser.args['ports']]
    threads = [t.start() for t in tasks]
    gevent.joinall(threads)

    print("Done!")
