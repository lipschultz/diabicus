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
    str_context = []
    for k, v in context.items():
        if isinstance(v, (list, tuple)):
            item = '<' + str(v[-5:]) + '>'
        else:
            item = repr(v)
        str_context.append(k + ' : ' + str(item))

    return '{' + ', '.join(str_context) + '}'

DEFAULT_MSG_FORMATTER = string.Formatter()

class BaseFact:
    def __init__(self):
        self.weight = 1
        self._messages = []
        self._messages_pos = 0

    def reset_messages(self):
        random.shuffle(self._messages)
        self._messages_pos = 0

    def get_default_message(self):
        return ''

    def message(self, formula, result, context):
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
            except OverflowError as e:
                logging.warning("Encountered overflow error for fact "+str(self)+", message " + msg + ", formula="+formula+", result="+result+", context="+context_to_str(context))

        self._messages_pos += prev_j + 1
        if looped or self._messages_pos >= len(self._messages):
            self.reset_messages()

        if return_message is None:
            return self.get_default_message()
        else:
            return return_message

class JsonFact(BaseFact):
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
    def load_file(clas, filename):
        with open(filename) as fin:
            contents = json.load(fin)

        facts = [clas(d) for d in contents]
        logging.info(str(len(facts)) + ' facts loaded from ' + filename)
        return NumberFacts(facts)

class NumberFacts:
    def __init__(self, facts):
        self.facts = facts

    def get_fact(self, formula, result, context):
        app_facts = self.find_applicable_facts(formula, result, context)
        rand_fact = self.pick_random_fact(app_facts)
        return rand_fact

    def find_applicable_facts(self, formula, result, context):
        app_facts = []
        for f in self.facts:
            if self.test_fact(f, formula, result, context):
                app_facts.append(f)

        logging.info("Number of applicable facts found: "+str(len(app_facts)))
        return app_facts

    def test_fact(self, fact, formula, result, context):
        timed_exec = time_limit.TimedExecution()
        try:
            logging.debug("Testing fact " + repr(fact) + " with context " + context_to_str(context))
            result = timed_exec.run(fact.test, formula, result, context)
            logging.debug("Test result for " + repr(fact) + ": " + str(result))
            return result
        except TimeoutError as e:
            logging.warning(str(fact) + ' timed out on formula = "'+formula+'", result = "' + str(result) + ', context = ' + context_to_str(context))
        except Exception as e:
            logging.warning(str(fact) + ' threw exception ' + repr(e) + ': formula = "'+formula+'", result = "' + str(result) + ', context = ' + context_to_str(context))

        return False

    def pick_random_fact(self, facts):
        logging.info("Pick random fact from: "+repr(facts))

        total = sum(f.weight for f in facts)
        if total == 0:
            logging.info('No facts to pick')
            return None

        p = random.uniform(0, total)
        cdf = 0
        for f in facts:
            cdf += f.weight
            if p <= cdf:
                logging.info('Fact picked: ' + str(f))
                return f

        f = random.choice(facts)
        logging.info('Fact picked (fallback): ' + str(f))
        return f

    def __len__(self):
        return len(self.facts)

    def __getitem__(self, key):
        return self.facts[key]
