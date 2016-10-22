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
                logging.warning("Encountered overflow error for fact "
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
        """
        Open file, read in facts, and create cls objects out of them,
        returning a NumberFacts object containing the facts.
        """
        with open(filename) as fin:
            contents = json.load(fin)

        facts = [cls(d) for d in contents]
        logging.info(str(len(facts)) + ' facts loaded from ' + filename)
        return NumberFacts(facts)

class NumberFacts:
    """
    A collection of facts and helper methods for picking facts.
    """
    def __init__(self, facts):
        self.facts = facts

    def get_fact(self, formula, result, context):
        """
        Return one fact that applies to the supplied formula, result, context.
        """
        app_facts = self.find_applicable_facts(formula, result, context)
        rand_fact = self.pick_random_fact(app_facts)
        return rand_fact

    def find_applicable_facts(self, formula, result, context):
        """
        Return all facts that apply to the given formula, result, context.
        """
        app_facts = [f for f in self.facts if self.test_fact(f, formula, result, context)]
        logging.info("Number of applicable facts found: "+str(len(app_facts)))
        return app_facts

    def test_fact(self, fact, formula, result, context):
        """
        Test whether fact applies to the supplied formula, result, context.
        """
        timed_exec = time_limit.TimedExecution()
        try:
            logging.debug("Testing fact " + repr(fact) + " with context " + context_to_str(context))
            result = timed_exec.run(fact.test, formula, result, context)
            logging.debug("Test result for " + repr(fact) + ": " + str(result))
            return result
        except TimeoutError as err:
            logging.warning(str(fact) + ' timed out on formula = "' + formula
                            +'", result = "' + str(result) + ', context = '
                            + context_to_str(context)
                           )
        except Exception as err:
            logging.warning(str(fact) + ' threw exception ' + repr(err)
                            + ': formula = "'+formula+'", result = "'
                            + str(result) + ', context = '
                            + context_to_str(context)
                           )

        return False

    def pick_random_fact(self, facts):
        """
        Pick a fact at random from facts, using a distribution that
        considers the weight of each fact.
        """
        logging.info("Pick random fact from: "+repr(facts))

        if len(facts) == 0:
            logging.info('No facts to pick')
            return None

        total = sum(fact.weight for fact in facts)
        if total == 0:
            rand_fact = random.choice(facts)
            logging.info('Total 0, picking factFact picked (fallback): '
                         + str(rand_fact)
                        )
            return rand_fact

        prob = random.uniform(0, total)
        cdf = 0
        for fact in facts:
            cdf += fact.weight
            if prob <= cdf:
                logging.info('Fact picked: ' + str(fact))
                return fact

        rand_fact = random.choice(facts)
        logging.info('Fact picked (fallback): ' + str(rand_fact))
        return rand_fact

    def __len__(self):
        return len(self.facts)

    def __getitem__(self, key):
        return self.facts[key]
