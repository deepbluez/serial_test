#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 20:54
# @remark 通信协议基础类库


class ProtocolBase(object):

    class Status:
        def __init__(self):
            self.init_error = None
            self.total = 0
            self.succeed = 0
            self.error_data = 0
            self.no_response = 0

    def __init__(self, args=None):
        self.args = args

        self.status = self.Status()

    def next_command(self):
        raise NotImplementedError()

    def validate_result(self, result):
        raise NotImplementedError()

    def _add_succeed(self):
        self.__add_total()
        self.status.succeed += 1

    def _add_no_response(self):
        self.__add_total()
        self.status.no_response += 1

    def _add_data_error(self):
        self.__add_total()
        self.status.error_data += 1

    def __add_total(self):
        self.status.total += 1


