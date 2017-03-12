#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 21:54
# @remark 解析测试器的命令行参数

"""
测试用例：
>>> ArgvParser(['tty=COM2;protocol= modbus', 'tty=COM3;protocol="modbus"']).actual_ports
{'COM3': [{'protocol': 'modbus'}], 'COM2': [{'protocol': 'modbus'}]}
"""

import re
import sys
import argparse


class ArgvParser(object):

    split_re = re.compile('[;]')
    key_split_re = re.compile('[=]')

    def __init__(self, argv=sys.argv):
        parser = argparse.ArgumentParser(description='串口测试程序')
        parser.add_argument('ports', nargs='+', help='需要测试的端口和配置项')
        parser.add_argument('--timeout', nargs='?', help='全局超时设置，覆盖默认设置')

        args = parser.parse_args(argv)
        self.actual_ports = {}
        self._process_args(args)

        self.args = {
            'timeout': args.timeout,
            'ports': self.actual_ports,
        }

    def _process_args(self, args):
        """
        Process and merge argv
        :param args: parsed argv
        :return: merged args
        """
        ports = [{a[0].strip(' \t\'"'): a[1].strip(' \t\'"') for a in (
            self.key_split_re.split(p2) for p2 in self.split_re.split(p) if p2.strip()
        )} for p in args.ports]

        for port in ports:
            if ',' not in port['tty']:
                port['tty'] += ',9600,8,N,1'

            tty_full = port['tty'].split(',')
            tty = tty_full[0]

            if tty not in self.actual_ports:
                self.actual_ports[tty] = {
                    'name': tty,
                    'baudrate': int(tty_full[1]),
                    'databits': int(tty_full[2]),
                    'parity': tty_full[3],
                    'stopbits': int(tty_full[4]),
                    'tests': [port]
                }
            else:
                self.actual_ports[tty]['tests'].append(port)
            del port['tty']


if __name__ == '__main__':
    import doctest

    doctest.testmod()
