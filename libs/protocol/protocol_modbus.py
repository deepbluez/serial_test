#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 23:56
# @remark modbus protocol simulate


"""
测试用例：
>>> ProtocolModbus({'id': 2, 'addr': '1', 'count': 3}).next_command()
'\\x02\\x03\\x00\\x01\\x00\\x03T8'
"""

from pymodbus import register_read_message
from pymodbus import transaction
from pymodbus import factory

from protocol_base import ProtocolBase


class ProtocolModbus(ProtocolBase):
    def __init__(self, args):
        super(ProtocolModbus, self).__init__(args)

        self.request = register_read_message.ReadHoldingRegistersRequest(
            address=int(args['addr']), count=int(args['count']), unit=int(args['id']))
        self.framer = transaction.ModbusRtuFramer(factory.ClientDecoder())

        self.message = self.framer.buildPacket(self.request)

    def next_command(self):
        return self.message

    def validate_result(self, command, result):
        if not result:
            self._add_no_response(command)
        else:
            self.framer.resetFrame()
            self.framer.addToFrame(result)
            if self.framer.checkFrame():
                self._add_succeed(command, result)
            else:
                self._add_data_error(command, result)


def create_protocol(args):
    return ProtocolModbus(args)

if __name__ == '__main__':
    import doctest

    doctest.testmod()
