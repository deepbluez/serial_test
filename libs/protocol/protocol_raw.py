#!/usr/bin/env python
# -*- encoding:utf-8 -*-

# @author James Wang
# @date   2017-03-12 23:56
# @remark modbus protocol simulate


"""
测试用例：
>>> ProtocolRaw({'command': '', 'validator_type': 'raw', 'validator': ''})._parse_hex_string('H e l l o 20 57 6f 72 6C 64 !')
'Hello World!'

>>> ProtocolRaw({'command': '123', 'validator_type': 'raw', 'validator': ''}).status.init_error
"Cant't parse '123', invalid hex string!"

>>> ProtocolRaw({'command': '', 'validator_type': 'regex', 'validator': '123[a-c]+'})._validate_regex('123abcccc')
True
>>> ProtocolRaw({'command': '', 'validator_type': 'regex', 'validator': '123[a-c]+$'})._validate_regex('123abccccd')
False

>>> ProtocolRaw({'command': '', 'validator_type': 'length', 'validator': '3'})._validate_length('abc')
True
>>> ProtocolRaw({'command': '', 'validator_type': 'length', 'validator': '9'})._validate_length('abc')
False

>>> ProtocolRaw({'command': '', 'validator_type': 'raw', 'validator': '123'}).status.init_error
"Cant't parse '123', invalid hex string!"
>>> ProtocolRaw({'command': '', 'validator_type': 'raw', 'validator': '41 42 C'})._validate_raw('ABC')
True
>>> ProtocolRaw({'command': '', 'validator_type': 'raw', 'validator': '41 42 C'})._validate_raw('abcd')
False

>>> ProtocolRaw({'command': '', 'validator_type': 'wildcard', 'validator': 'A?C'})._validate_wildcard('ABC')
True
>>> ProtocolRaw({'command': '', 'validator_type': 'wildcard', 'validator': 'A?C'})._validate_wildcard('ABBC')
False

"""

import re

from protocol_base import ProtocolBase
from libs.fields import *


class ProtocolRaw(ProtocolBase):

    split_re = re.compile('[ ]+')
    hexchar_re = re.compile('^[a-f0-9]{2}$', re.IGNORECASE)

    def __init__(self, args):
        super(ProtocolRaw, self).__init__(args)

        self.command = self._parse_hex_string(args[f_command])
        self.validator_type = args[f_validator_type]
        if self.validator_type not in ('regex', 'length', 'raw', 'wildcard'):
            self.status.init_error = "Invalid validator type: '%s'!" % self.validator_type
        self.validator = args[f_validator]
        if self.validator_type == 'regex':
            self.__validator_func = self._validate_regex
        elif self.validator_type == 'length':
            self.__validator_func = self._validate_length
        elif self.validator_type == 'raw':
            self.__validator_func = self._validate_raw
        else:
            self.__validator_func = self._validate_wildcard

        # 强制调用一次，使对应的解析器处理参数
        self.__validator_func(None)

    def next_command(self):
        return self.command

    def validate_result(self, result):
        if not result:
            self._add_no_response()
        else:
            if self.__validator_func(result):
                self._add_succeed()
            else:
                self._add_data_error()

    def _parse_hex_string(self, orig_text):
        result = ''
        for c in self.split_re.split(orig_text):
            if len(c) == 1:
                result += c
            elif self.hexchar_re.match(c):
                result += chr(int(c, base=16))
            elif not c:
                pass
            else:
                self.status.init_error = "Cant't parse '%s', invalid hex string!" % orig_text
        return result

    @staticmethod
    def _translate(pat):
        """Translate a shell PATTERN to a regular expression.

        There is no way to quote meta-characters.
        NOTE: from lib/fnmatch.py
        """

        i, n = 0, len(pat)
        res = ''
        while i < n:
            c = pat[i]
            i += 1
            if c == '*':
                res += '.*'
            elif c == '?':
                res += '.'
            elif c == '[':
                j = i
                if j < n and pat[j] == '!':
                    j += 1
                if j < n and pat[j] == ']':
                    j += 1
                while j < n and pat[j] != ']':
                    j += 1
                if j >= n:
                    res += '\\['
                else:
                    stuff = pat[i:j].replace('\\', '\\\\')
                    i = j + 1
                    if stuff[0] == '!':
                        stuff = '^' + stuff[1:]
                    elif stuff[0] == '^':
                        stuff = '\\' + stuff
                    res = '%s[%s]' % (res, stuff)
            else:
                res = res + re.escape(c)
        return res + '\Z(?ms)'

    def _validate_length(self, result):
        if not result:
            self.validator = int(self.validator)
            return False
        else:
            return len(result) == self.validator

    def _validate_regex(self, result):
        if not result:
            self.validator = re.compile(str(self.validator))
            return False
        else:
            return bool(self.validator.match(result))

    def _validate_raw(self, result):
        if not result:
            self.validator = self._parse_hex_string(self.validator)
            return False
        else:
            return self.validator == result

    def _validate_wildcard(self, result):
        if not result:
            self.validator = re.compile(self._translate(str(self.validator)))
            return False
        else:
            return bool(self.validator.match(result))


def create_protocol(args):
    return ProtocolRaw(args)

if __name__ == '__main__':
    import doctest

    doctest.testmod()
