from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from simpleeval import SimpleEval
import compute
import math
import time
import number_facts
import argparse

DISCO_LENGTH = 2 #seconds

class CalcMainLayout(BoxLayout):
    pass

class Disco:
    def __init__(self, default_length=DISCO_LENGTH):
        self.__stop_time = 0
        self.__default_len = default_length

    def update_stop_time(self, length=None):
        if length is None:
            length = self.__default_len
        self.__stop_time = length + time.time()

    def is_discoing(self):
        return time.time() < self.__stop_time

class Calculator:
    def __init__(self):
        self._result = 0
        self._input = ''
        self._output = ''

        self.__eval = SimpleEval()
        self.__init_eval()

        self._output_format = {complex : lambda v : '%0.8g + %0.8gi' % (v.real, v.imag),
                               float : lambda v : "%0.8g" % v,
                               str : lambda v : v
                               }
        self._output_format[int] = self._output_format[float]

        self.__just_calculated = False
        self.__disco = Disco()

        self.context = {'result' : [], 'formula' : [], 'output' : []}

    def __init_eval(self):
        self.__eval.names['Ans'] = self._result
        self.__eval.functions['ln'] = math.log

    def get_input(self):
        return self._input
    def set_input(self, value):
        self._input = value
    input = property(get_input, set_input)
    def _append_input_text(self, text):
        self.input += text

    def get_result(self):
        return self._result
    def set_result(self, value):
        self._result = value
        self.__eval.names['Ans'] = value
    result = property(get_result, set_result)

    def get_output(self):
        return self._output
    def set_output(self, value):
        self._output = self._output_format[type(value)](value)
        return self._output
    output = property(get_output, set_output)

    def get_context(self):
        return self.__context

    def start_disco(self):
        if not self.__disco.is_discoing():
            Clock.schedule_interval(self.update_disco, 0.25)
        self.__disco.update_stop_time()

    def update_disco(self, dt):
        return self.__disco.is_discoing()

    def __on_interaction(self):
        self.start_disco()

    def press_key(self, value):
        self.__on_interaction()
        if self.__just_calculated:
            self.clear()
        self.__just_calculated = False
        if len(self.input) == 0 and value in ('×', '/', '^'):
            self.press_ans()
        self._append_input_text(str(value))

    def press_ans(self):
        self.press_key("Ans")

    def press_function_key(self, func_name):
        self.__on_interaction()
        if self.__just_calculated:
            self.clear()
        self.__just_calculated = False
        self.input += compute.FUNCTION_PREFIX + func_name + '('

    def clear(self):
        self.__on_interaction()
        if len(self.input) == 0:
            self.output = ''
        else:
            self.input = ''

    def bksp(self):
        self.__on_interaction()
        self.__just_calculated = False
        if len(self.input) > 0:
            if self.input[-3:] == 'Ans':
                self.input = self.input[:-3]
            elif len(self.input) > 1 and self.input[-1] == '(' and self.input[-2].isalpha():
                start_of_function = self.input.rfind(compute.FUNCTION_PREFIX)
                self.input = self.input[:start_of_function]
            else:
                self.input = self.input[:-1]

    def calculate(self):
        self.__on_interaction()
        result = compute.eval_expr(self.__eval, self.input)
        if isinstance(result, compute.ComputationError):
            self.output = "Error: "+result.msg
        else:
            self.result = result
            self.output = result
        self.__just_calculated = True
        self.context['result'].append(result)
        self.context['formula'].append(self.input)
        self.context['output'].append(self.output)
        return result

class CalcApp(App, Calculator):
    def __init__(self, *args, **kwargs):
        self.__facts = kwargs.get('facts')
        del kwargs['facts']

        super(CalcApp, self).__init__(*args, **kwargs)

        self._answer_format = {complex : lambda v : '%0.2g + %0.2gi' % (v.real, v.imag),
                               float : lambda v : "%0.4g" % v
                               }
        self._answer_format[int] = self._answer_format[float]

    def build(self):
        return CalcMainLayout()

    def get_input(self):
        return self.root.ids.input.text
    def set_input(self, value):
        self.root.ids.input.text = value
    input = property(get_input, set_input)

    def get_output(self):
        return self.root.ids.output.text
    def set_output(self, value):
        self.root.ids.output.text = super(CalcApp, self).set_output(value)
    output = property(get_output, set_output)

    def get_result(self):
        return super(CalcApp, self).get_result()
    def set_result(self, value):
        super(CalcApp, self).set_result(value)
        display_value = self._answer_format[type(value)](value)
        self.root.ids.basic_keypad.ids.answer_button.text = 'Ans\n[size=16](%s)[/size]' % (display_value)
    result = property(get_result, set_result)

    def __set_clear_button(self, to_all_clear=False):
        pass

    def calculate(self):
        result = super(CalcApp, self).calculate()
        if self.__facts is not None:
            fact = number_facts.get_fact(self.__facts, self.input, result, self.context)
            if fact is not None:
                self.root.ids.fact.text = "[ref='" + fact.link + "']" + fact.message(self.input, result, self.context) + "[/ref]"

def command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--facts', help="Path to json file containing facts and when to use them")
    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = command_line_arguments()
    facts = None
    if args.facts is not None:
        facts = number_facts.load_json_file(args.facts)
    CalcApp(facts=facts).run()
