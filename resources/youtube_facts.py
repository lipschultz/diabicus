"""
Diabicus: A calculator that plays music, lights up, and displays facts.
Copyright (C) 2016 Michael Lipschultz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from fractions import Fraction
import math
import sys
import itertools
import os
import random
import re

import scipy.integrate

from src import number_facts
from src import format_numbers
from src.numeric_tools import *

class YoutubeFact(number_facts.JsonFact):
    """
    Class to hold a fact from a Youtube video.
    """
    def __init__(self, json_data):
        super(YoutubeFact, self).__init__(json_data)
        self.link = json_data.get('link')
        self.title = json_data.get('title')
        self.host = json_data.get('host')
        self.date = json_data.get('date')
        self.source = json_data.get('source')
        self.oeis = json_data.get('oeis')
        self.wiki = json_data.get('wiki')
        self.weight = json_data.get('weight', 1)
        self.init = json_data.get('init')

        try:
            self.test = eval(self.raw_test)
        except Exception:
            self.test = False
        if not callable(self.test):
            self.test = lambda *args: False

        if not hasattr(self.raw_message, '__iter__') or isinstance(self.raw_message, str):
            self.raw_message = [self.raw_message]

        for i in range(len(self.raw_message)):
            raw_msg = self.raw_message[i]
            try:
                msg = eval(raw_msg)
            except Exception:
                msg = raw_msg
            if not callable(msg):
                if raw_msg is None:
                    raw_msg = self.title
                msg = lambda formula, result, context: \
                    number_facts.DEFAULT_MSG_FORMATTER.format(raw_msg,
                                                              formula=formula,
                                                              result=result,
                                                              context=context
                                                             )

            self._messages.append(msg)

        try:
            self.init = compile(self.init, '<json_string>', "exec")
            print("eval result for", self.title, ":", eval(self.init, globals(), locals()))
        except Exception:
            pass

    def get_default_message(self):
        """
        Use the title of the video as the default message for a fact.
        """
        return self.title

    def __str__(self):
        return self.title

    def __repr__(self):
        return str(self) + "{test : " + repr(self.raw_test.encode("unicode-escape")) + "}"

def farey_addition(context):
    """
    Perform Farey addition on previous and previous-third result and
    return True if it equals the previous-second result.
    """
    if len(context['result']) < 3 or any(not is_rational(r) for r in context['result'][-3:]):
        return False
    first = Fraction(context['result'][-3]).limit_denominator(234)
    second = Fraction(context['result'][-2]).limit_denominator(234)
    third = Fraction(context['result'][-1]).limit_denominator(234)
    return Fraction(first.numerator + third.numerator,
                    first.denominator + third.denominator
                   ) == second

def int_to_digits(result, as_type=int):
    """ Convert result into a list of digits. """
    if as_type == int:
        return [result // 10**i % 10 for i in range(math.ceil(math.log(result, 10)))]
    else:
        return list(str(result))

def vampire(result):
    """
    Returns True if result is a Vampire number.

    A vampire number is an integer whose digits, when used to form two
    integers (of equal length) that are then multiplied together, give
    back the original number, e.g. 1260 = 21*60.
    """
    digits = int_to_digits(result, str)
    result_size = len(digits)
    partition_template = [1]*(result_size//2) + [0]*(result_size//2)
    partitions = set([v for v in itertools.permutations(partition_template)])
    for part in partitions:
        fang1 = int(''.join(itertools.compress(digits, part)))
        fang2 = int(''.join(itertools.compress(digits, [-1*v+1 for v in part])))
        print(fang1, '*', fang2, '=', fang1*fang2, '?=', result)
        if fang1*fang2 == result:
            return True
    return False

class MagicSquare(YoutubeFact):
    """
    Creates a magic square out of the result.
    """
    def __init__(self):
        self.link = 'https://www.youtube.com/watch?v=aQxCnmhqZko'
        self.title = 'Magic Square Party Trick'
        self.source = 'Numberphile'
        self.skip = True

        self.__coeff = 1/(4*math.sqrt(3))
        self.__exp = math.pi*math.sqrt(2/3)

    def test(self, formula, result, context):
        """
        Returns True if the magic square fact applies for the given result.
        """
        return not self.skip and is_int(result) and 21 <= result <= 65

    def message(self, formula, result, context):
        """
        The message to display if the fact applies to the current context.
        """
        row1 = [result-20, 1, 12, 7]
        row2 = [11, 8, result-21, 2]
        row3 = [5, 10, 3, result-18]
        row4 = [4, result-19, 6, 9]
        square = [row1, row2, row3, row4]
        return 'The magic square for %d is %s' % (result, square)

def load_facts():
    """
    Loads facts from the file youtube.json (in the same location as this
    python module and returns a number_facts.NumberFacts object
    containing them.
    """
    path = os.path.dirname(__file__)
    return YoutubeFact.load_file(os.path.join(path, 'youtube.json'))
