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

import logging
import json
import random

from .. import time_limit


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

class CaseCollection:
    """
    A collection of cases and helper methods for picking cases.
    """
    def __init__(self, cases):
        self.cases = cases

    def get_case(self, formula, result, context):
        """
        Return one case that applies to the supplied formula, result, context.
        """
        app_cases = self.find_applicable_cases(formula, result, context)
        rand_case = self.pick_random_case(app_cases)
        return rand_case

    def find_applicable_cases(self, formula, result, context):
        """
        Return all cases that apply to the given formula, result, context.
        """
        app_cases = [f for f in self.cases if self.test_case(f, formula, result, context)]
        logging.info("CaseCollection.find_applicable_cases: "
                     +"Number of applicable cases found: "
                     +str(len(app_cases))
                    )
        return app_cases

    def test_case(self, case, formula, result, context):
        """
        Test whether case applies to the supplied formula, result, context.
        """
        timed_exec = time_limit.TimedExecution()
        try:
            logging.debug("CaseCollection.test_case: " + repr(case)
                          + " with context " + context_to_str(context)
                         )
            result = timed_exec.run(case.test, formula, result, context)
            logging.debug("CaseCollection.test_case: Result for " + repr(case) + ": " + str(result))
            return result
        except TimeoutError as err:
            logging.warning('CaseCollection.test_case: ' + str(case)
                            + ' timed out on formula = "' + formula
                            +'", result = "' + str(result)
                            + ', context = ' + context_to_str(context)
                           )
        except Exception as err:
            logging.warning('CaseCollection.test_case: ' + str(case) + ' threw exception ' + repr(err)
                            + ': formula = "'+formula+'", result = "'
                            + str(result) + ', context = '
                            + context_to_str(context)
                           )

        return False

    def pick_random_case(self, cases):
        """
        Pick a case at random from cases, using a distribution that
        considers the weight of each case.
        """
        logging.info("CaseCollection.pick_random_case: From: "+repr(cases))

        if len(cases) == 0:
            logging.info('CaseCollection.pick_random_case: No cases to pick')
            return None

        total = sum(case.weight for case in cases)
        if total == 0:
            rand_case = random.choice(cases)
            logging.info('CaseCollection.pick_random_case: Total 0, picking case'
                         + str(rand_case)
                        )
            return rand_case

        prob = random.uniform(0, total)
        cdf = 0
        for case in cases:
            cdf += case.weight
            if prob <= cdf:
                logging.info('CaseCollection.pick_random_case: Picked ' + str(case))
                return case

        rand_case = random.choice(cases)
        logging.info('CaseCollection.pick_random_case: Picked (fallback): ' + str(rand_case))
        return rand_fact

    def __len__(self):
        return len(self.cases)

    def __getitem__(self, key):
        return self.cases[key]


def load_json_cases(cls, filename):
    """
    Open file, read in cases, and create cls objects out of them,
    returning a CaseCollection object containing the cases.
    """
    with open(filename) as fin:
        contents = json.load(fin)

    cases = [cls(d) for d in contents]
    logging.info('load_json_cases: ' + str(len(cases)) + ' cases loaded from ' + filename)
    return CaseCollection(cases)
