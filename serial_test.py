#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 21:53
# @remark 串口测试入口程序

import sys
import gevent

from gevent import monkey
monkey.patch_all()

from libs.argv_parser import ArgvParser
from libs.task_runner import TaskRunner
from libs.fields import *
from libs.thirdparty.termcolor2 import colored


tasks = []
threads = []
verbose = False


def show_status():
    def pretty_show_bytes(item):
        def format_hex(io_bytes, title):
            if not io_bytes:
                return '  %s ' % title + colored('<Empty>', 'red')
            r_ = '  ' + title + '\n    '
            chr_line = ''
            for idx, b in enumerate(io_bytes):
                r_ += '%02X' % ord(b) + ('  ' if (idx + 1) % 4 == 0 else ' ')
                chr_line += b if 32 <= ord(b) < 127 else '.'
                if (idx + 1) % 8 == 0 or (idx + 1) == len(io_bytes):
                    pad_spaces = '<.>' * (0 if (idx + 1) % 8 == 0 else -((idx + 1) % 8 - 8)) +\
                                 ('  ' if 0 < ((idx + 1) % 8) <= 4 else ('' if (idx + 1) % 8 == 0 else ' '))
                    r_ += pad_spaces + '   ' + chr_line
                    chr_line = ''
                    if (idx + 1) != len(io_bytes):
                        r_ += '\n    '
            return r_

        return format_hex(item[f_command], "Send:") + '\n' + format_hex(item[f_response], "Recv:")
    while True:
        result = ''
        for task in tasks:
            result += '%(name)s, %(baudrate)d, %(databits)d, %(parity)s, %(stopbits)d\n' % {
                f_name: task.tests[f_name],
                f_baudrate: task.tests[f_baudrate],
                f_databits: task.tests[f_databits],
                f_parity: task.tests[f_parity],
                f_stopbits: task.tests[f_stopbits],
            }
            for protocol in task.protocols:
                total = protocol.status.total if protocol.status.total != 0 else 1
                result += ''.join([
                    '  %s:' % colored(protocol.args[f_name]),
                    'Total:%4d' % protocol.status.total,
                    colored(' Succeed:%4d(%3d%%)' %
                            (protocol.status.succeed, protocol.status.succeed * 100 / total), 'green'),
                    colored(' Format Error:%4d(%3d%%)' %
                            (protocol.status.error_data, protocol.status.error_data * 100 / total), 'red'),
                    colored(' Empty:%4d(%3d%%)' %
                            (protocol.status.no_response, protocol.status.no_response * 100 / total), 'magenta'),
                    '\n',
                ])
                if verbose:
                    result += '\n\n'.join(map(pretty_show_bytes, protocol.status.io_bytes))
                    result += '\n\n'
                protocol.status.io_bytes = []
        print(result)
        gevent.sleep(3)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python serial_test.py <config_file> [-v|--verbose]")
        sys.exit(1)

    verbose = True if '-v' in sys.argv or '--verbose' in sys.argv else verbose

    with open(sys.argv[1], 'r') as f:
        config_lines = [l for l in (l.strip() for l in f.readlines()) if l and not l.startswith('#')]

    argv_parser = ArgvParser(config_lines)
    tasks = [TaskRunner(argv_parser.args, port) for port in argv_parser.args['ports']]
    threads = [t.start() for t in tasks]
    threads.append(gevent.spawn(show_status))
    gevent.joinall(threads)

    print("Done!")
