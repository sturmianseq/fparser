#!/usr/bin/env python

# All rights reserved.

# Modifications made as part of the fparser project are distributed
# under the following license:

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""C99 Preprocessor Syntax Rules.
"""
# Original author: Balthasar Reuter <balthasar.reuter@ecmwf.int>
# Based on previous work by Martin Schlipf (https://github.com/martin-schlipf)
# First version created: Jan 2020

import re
import logging

from fparser.two.utils import Base, InternalError
from fparser.two.Fortran2003 import Include_Filename

#
# ISO/IEC 9899: 1999 (C99)
#

#
# Section 6.10 Preprocessing directives
#

def match_cpp_directive(content, reader):
    cls_list = (Cpp_Include_Stmt,)
    for cls in cls_list:
        obj = cls(reader)
        if obj:
            return obj
    return obj


# 6.10.1 Conditional inclusion


class Cpp_Include_Stmt(Base):  # 6.10.2 Source file inclusion
    """
    C99 section 6.10.2 Source file inclusion
    include_stmt is # include [ <h-char-sequence>
                              | "q-char-sequence"
                              | pp-tokens ] new-line
    """

    _regex = re.compile(r"#\s*include\b")

    use_names = ['Include_Filename']

    @staticmethod
    def match(string):
        '''Implements the matching for an include statement.

        :param str string: the string to match with as an include statement.
        :returns: a tuple of size 1 containing a Cpp_Include_Filename \
        object with the matched filename if there is a match, or None \
        if there is not.
        :rtype: (:py:class:`fparser.two.Fortran2003.Include_Filename`) \
        or NoneType
        '''

        if not string:
            return None

        line = string.strip()
        found = Cpp_Include_Stmt._regex.match(line)
        if not found:
            # The line does not match an include statement
            return None
        rhs = line[found.end():].strip()
        if rhs is None or len(rhs) < 3:
            # Either we didn't find any includes or the content after
            # the include token is too short to be valid (it must at
            # least contain quotes and one character.
            return None
        if not (rhs[0] == '"' and rhs[-1] == '"'):
            # The filename should be surrounded by single or double
            # quotes but this is not the case.
            return None
        # Remove the quotes.
        file_name = rhs[1:-1]
        # Pass the potential filename to the relevant class.
        name = Include_Filename(file_name)
        if not name:
            raise InternalError(
                "C99Preprocessor.py:Cpp_Include_Stmt:match Include_Filename "
                "should never return None or an empty name")
        return (name,)

    def tostr(self):
        '''
        :return: this include_stmt as a string
        :rtype: str
        '''
        return '#include "{}"'.format(self.items[0])
