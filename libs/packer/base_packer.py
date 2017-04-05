#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 16:38
# @remark 基础包组合类，为特定协议的包组合提供基础支持接口


class BasePacker(object):
    def __init__(self, params, ):
        self.params = params

    def generate_command(self, cmdid=None):
        raise NotImplementedError()
