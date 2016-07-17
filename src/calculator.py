from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import ast
import operator
import re
from simpleeval import SimpleEval
import math

FUNCTION_PREFIX = '\u200b'
DISCO_LENGTH = 2 #seconds

class ComputationError:
    def __init__(self, message):
        self.msg = message

EXPRESSION_TRANSLATIONS = {'×' : '*', '^': '**'}
def translate_operators(expr):
    for k, v in EXPRESSION_TRANSLATIONS.items():
        expr = expr.replace(k, v)
    return expr

def make_operations_explicit(expr):
    expr = re.sub(r'([0-9).]?)\(', lambda m: '(' if len(m.group(1)) == 0 else m.group(1)+'*(', expr)
    expr = re.sub('([0-9).]?)'+FUNCTION_PREFIX, lambda m: '' if len(m.group(1)) == 0 else m.group(1)+'*', expr)
    return expr

def eval_expr(evaluator, expr):
    expr = translate_operators(expr)
    expr = make_operations_explicit(expr)
    try:
        return evaluator.eval(expr)
    except SyntaxError:
        return ComputationError('invalid syntax')
    except ZeroDivisionError:
        return ComputationError('divide by zero')
    except:
        return ComputationError('computation error')

class CalcMainLayout(BoxLayout):
    pass

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
    def input_function(self, func_name):
        self.input += FUNCTION_PREFIX + func_name + '('

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

    def press_key(self, value):
        if self.__just_calculated:
            self.clear()
        self.__just_calculated = False
        if len(self.input) == 0 and value in ('*', '/', '^'):
            self.press_ans()
        self._append_input_text(str(value))

    def press_ans(self):
        self.press_key("Ans")

    def clear(self):
        if len(self.input) == 0:
            self.output = ''
        else:
            self.input = ''

    def bksp(self):
        self.__just_calculated = False
        if len(self.input) > 0:
            if self.input[-3:] == 'Ans':
                self.input = self.input[:-3]
            else:
                self.input = self.input[:-1]

    def calculate(self):
        result = eval_expr(self.__eval, self.input)
        if isinstance(result, ComputationError):
            self.output = "Error: "+result.msg
        else:
            self.result = result
            self.output = result
        self.__just_calculated = True

class CalcApp(App, Calculator):
    def __init__(self, *args, **kwargs):
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

    def __on_interaction(self):
        pass

    def __set_clear_button(self, to_all_clear=False):
        pass

    def press_ln(self):
        self.input_function('ln')


if __name__=="__main__":
    CalcApp().run()
