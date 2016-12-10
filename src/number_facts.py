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

import random
import logging
import string
import json

from . import time_limit
from . import cases

def context_to_str(context):
    """ Convert context into a string useful for logging. """
    str_context = []
    for k, val in context.items():
        if isinstance(val, (list, tuple)):
            item = '<' + str(val[-5:]) + '>'
        else:
            item = repr(val)
        str_context.append(k + ' : ' + str(item))

    return '{' + ', '.join(str_context) + '}'

DEFAULT_MSG_FORMATTER = string.Formatter()

class BaseFact:
    """
    Base Fact class

    Fact classes will test whether a given context applies for the fact
    and if it does, what message to display.

    This base class is intended to be overridden by classes to load and
    hold specific facts.
    """
    def __init__(self):
        self.weight = 1
        self._messages = []
        self._messages_pos = 0

    def reset_messages(self):
        """
        Reset messages by shuffling order and setting message position to 0.

        When all messages have been used (or skipped if they caused an
        exception), "reset" them to be used again.  By shuffling, each
        message should have a more equal chance of being chosen.
        """
        random.shuffle(self._messages)
        self._messages_pos = 0

    def get_default_message(self):
        """
        Default message to use if the fact is applicable (i.e. the test
        passes), but none of the messages work (perhaps because they all
        raised an exception).
        """
        return ''

    def message(self, formula, result, context):
        """ Pick a message from the object. """
        looped = False
        prev_j = -1
        return_message = None
        for i in range(len(self._messages)):
            j = (i+self._messages_pos) % len(self._messages)
            looped = looped or prev_j > j
            prev_j += 1

            msg = self._messages[j]
            try:
                return_message = msg(formula, result, context)
                break
            except OverflowError:
                logging.warning("BaseFact.message: Encountered overflow error for fact "
                                +str(self)+", message " + msg + ", formula="+formula
                                +", result="+result+", context="+context_to_str(context)
                               )

        self._messages_pos += prev_j + 1
        if looped or self._messages_pos >= len(self._messages):
            self.reset_messages()

        if return_message is None:
            return self.get_default_message()
        else:
            return return_message

class JsonFact(BaseFact):
    """
    A fact class where the facts are loaded from JSON data.
    """
    def __init__(self, json_data):
        super(JsonFact, self).__init__()
        self.json_data = json_data
        self.raw_test = json_data.get('test')
        self.raw_message = json_data.get('msg')

    def __str__(self):
        return self.raw_test.encode("unicode-escape") + " -> " + self.raw_message

    def __repr__(self):
        return self.json_data

    @classmethod
    def load_file(cls, filename):
        return cases.load_json_cases(cls, filename)
