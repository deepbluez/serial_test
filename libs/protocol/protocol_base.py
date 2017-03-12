#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 20:54
# @remark 通信协议基础类库


class ProtocolBase(object):
    def __init__(self, args=None):
        self.args = args

    def next_command(self):
        raise NotImplementedError()

    def validate_result(self, result):
        raise NotImplementedError()
