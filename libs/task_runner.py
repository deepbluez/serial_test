#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 21:13
# @remark  创建并执行测试任务

import gevent
import serial


class TaskRunner(object):
    def __init__(self, args, current_port):
        self.args = args

        # Serial read timeout, default 300ms
        self.read_timeout = int(self.args.get('timeout')) if args.get('timeout') else 300
        # Serial port name, must specify from args
        self.serial_port = current_port

        self.tests = self.args['ports'][current_port]
        self.protocols = []

        self._load_protocol()

        self.serial = None

    def start(self):
        def _parity(cfg):
            if cfg == 'E':
                return serial.PARITY_EVEN
            elif cfg == 'O':
                return serial.PARITY_ODD
            elif cfg == 'M':
                return serial.PARITY_MARK
            elif cfg == 'S':
                return serial.PARITY_SPACE
            else:
                return serial.PARITY_NONE

        self.serial = serial.Serial(self.serial_port, self.tests['baudrate'], bytesize=self.tests['databits'],
                                    parity=_parity(self.tests['parity']),
                                    stopbits=self.tests['stopbits'], timeout=self.read_timeout / 1000.0)
        runner_thread = gevent.spawn(self._task_thread)
        return runner_thread

    def _load_protocol(self):
        import importlib
        for test in self.tests['tests']:
            module_name = '.protocol.protocol_' + test['protocol']
            protocol_module = importlib.import_module(module_name, 'libs')
            protocol_factory = getattr(protocol_module, 'create_protocol', None)
            self.protocols.append(protocol_factory(test))

    def _task_thread(self):
        while True:
            for protocol in self.protocols:
                self.serial.write(protocol.next_command())
                result = self.serial.read(1024 * 1024)
                print "%s is %r(%s)" % (self.serial_port, protocol.validate_result(result), result)
                gevent.sleep(0)
