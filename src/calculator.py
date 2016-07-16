from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import simpleeval

DISCO_LENGTH = 2 #seconds

class ComputationError:
    def __init__(self, message):
        self.msg = message

def eval_expr(expr, ans):
    try:
        return simpleeval.simple_eval(expr, names={"Ans" : ans})
    except SyntaxError:
        return ComputationError('invalid syntax')
    except ZeroDivisionError:
        return ComputationError('divide by zero')

class CalcMainLayout(BoxLayout):
    pass

class Calculator:
    def __init__(self):
        self._result = 0
        self._input = ''
        self._output = ''

        self._output_format = {complex : lambda v : '%0.8g + %0.8gi' % (v.real, v.imag),
                               float : lambda v : "%0.8g" % v,
                               str : lambda v : v
                               }
        self._output_format[int] = self._output_format[float]

        self.__just_calculated = False

    def get_input(self):
        return self._input
    def set_input(self, value):
        self._input = value
    input = property(get_input, set_input)
    def _append_input_text(self, text):
        self.input = self.input + text

    def get_result(self):
        return self._result
    def set_result(self, value):
        self._result = value
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
        self._append_input_text(str(value))

    def press_ans(self):
        self.press_key("Ans")

    def clear(self):
        if len(self.input) == 0:
            self.output = ''
        else:
            self.input = ''

    def calculate(self):
        result = eval_expr(self.input, ans=self.result)
        if isinstance(result, ComputationError):
            self.output = "Error: "+result.msg
        else:
            self.result = result
            self.output = result
        self.__just_calculated = True

class CalcApp(App, Calculator):
    def __init__(self, *args, **kwargs):
        super(CalcApp, self).__init__(*args, **kwargs)
        self.__equals_pressed = False

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

    def __on_interaction(self):
        pass

    def __set_clear_button(self, to_all_clear=False):
        pass

    def press_ln(self):
        pass

    def calculate(self):
        super(CalcApp, self).calculate()
        self.__equals_pressed = True

    def bksp(self):
        pass


if __name__=="__main__":
    CalcApp().run()
