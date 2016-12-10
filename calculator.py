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

import math
import time
import argparse
import logging
import glob
import random
import os
import importlib

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

from src.simpleeval import SimpleEval
from src import compute
from src import numeric_tools
from src import time_limit
from src import format_numbers

DISCO_LENGTH = 5 #seconds

def get_loader_lib(module_location):
    path, name = os.path.split(module_location)
    module_name = os.path.splitext(name)[0]
    module_path = path
    importlib.import_module(module_path)
    return importlib.import_module('.'+module_name, module_path)

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
    def __init__(self, disco_length=DISCO_LENGTH):
        self._result = 0
        self._input = ''
        self._output = ''

        self.__eval = SimpleEval()
        self.__init_eval()

        self.__DISPLAY_DIGITS = 8
        self._output_format = {complex : lambda v : format_numbers.pretty_print_complex(format_numbers.simplify_complex(v), lambda n: format_numbers.to_pretty_x10(n, self.__DISPLAY_DIGITS)),
                               float : lambda v : format_numbers.to_pretty_x10(v, 2*self.__DISPLAY_DIGITS),#"%0.8g" % v,
                               str : lambda v : v
                               }
        self._output_format[int] = self._output_format[float]

        self.__just_calculated = False
        self.__disco = Disco(default_length=disco_length)

        self.context = {'result' : [], 'formula' : [], 'output' : []}

    def __init_eval(self):
        self.__eval.names['Ans'] = self._result
        self.__eval.names['π'] = math.pi
        self.__eval.names['τ'] = 2*math.pi
        self.__eval.names['e'] = math.e
        self.__eval.names['i'] = numeric_tools.I
        self.__eval.names['φ'] = numeric_tools.GOLDEN_RATIO
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
        return self.context

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
        logging.info('Calculator.calculate: input = '+self.input)
        result = compute.eval_expr(self.__eval, self.input)
        logging.info('Calculator.calculate: result = '+str(result))
        if isinstance(result, compute.ComputationError):
            self.output = "Error: "+result.msg
        else:
            self.result = result
            self.output = result
        self.__just_calculated = True
        logging.info('Calculator.calculate: output = '+str(self.output))
        self.context['result'].append(result)
        self.context['formula'].append(self.input)
        self.context['output'].append(self.output)
        return result

class CalcApp(App, Calculator):
    def __init__(self, *args, **kwargs):
        self.__facts = kwargs.get('facts')
        del kwargs['facts']

        self.__audio = kwargs.get('audio_src', [])
        del kwargs['audio_src']
        self.__audio_current = None
        self.__audio_current_pos = 0
        self.__audio_current_len = math.inf
        self.__audio_current_state = None
        
        self.__special_music = kwargs.get('special_music')
        if self.__special_music is not None:
            special_music_lib = get_loader_lib(self.__special_music)
            self.__special_music = special_music_lib.load()
            del kwargs['special_music']
        self.__special_music_current = None

        super(CalcApp, self).__init__(*args, **kwargs)

        self._answer_format = {complex : lambda v: format_numbers.pretty_print_complex(format_numbers.simplify_complex(v), lambda n: format_numbers.to_pretty_x10(n, 2)),#lambda v : '%0.1g + %0.2gi' % (v.real, v.imag),
                               float : lambda v : "%0.4g" % v
                               }
        self._answer_format[int] = self._answer_format[float]

        self.timed_exec = time_limit.TimedExecution()

    def __init_eval(self):
        super(CalcApp, self).__init_eval()
        del self.__eval.names['True']
        del self.__eval.names['False']

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

    def __play_new_audio(self):
        choice = random.choice(self.__audio)
        self.__audio_current = SoundLoader.load(choice)
        self.__audio_current.play()
        self.__audio_current_pos = 0
        self.__audio_current_len = self.__audio_current.length
        self.__audio_current_state = 'play'

    def update_disco(self, dt):
        do_play = super(CalcApp, self).update_disco(dt)
        if do_play:
            if self.__audio_current is None or (self.__audio_current_state == 'play' and self.__audio_current.state == 'stop'):
                self.__play_new_audio()
            elif self.__audio_current_state == 'paused':
                self.__audio_current.play()
                time.sleep(0.1)
                self.__audio_current.seek(self.__audio_current_pos)
                self.__audio_current_state = 'play'
        else:
            self.__pause_disco()

    def __pause_disco(self):
        if self.__audio_current.state == 'play':
            self.__audio_current_len = self.__audio_current.length
            self.__audio_current_pos = self.__audio_current.get_pos()
            self.__audio_current_state = 'paused'
            self.__audio_current.stop()

    def calculate(self):
        result = super(CalcApp, self).calculate()
        if self.__facts is not None:
            fact = self.__facts.get_case(self.input, result, self.context)
            if fact is not None:
                message = fact.title
                try:
                    message = self.timed_exec.run(fact.message, self.input, result, self.context)
                except TimeoutError as e:
                    logging.warn('CalcApp.calculate: Getting message timed out for fact '+str(fact))

                self.root.ids.fact.text = "[ref='" + fact.link + "']" + message + "[/ref]"
        if self.__special_music is not None:
            smusic = self.__special_music.get_case(self.input, result, self.context)
            self.__pause_disco()
            self.__special_music_current = SoundLoader.load(smusic.filename)
            self.__special_music_current.play()

def command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disco-length', default=DISCO_LENGTH, type=float, help="Number of seconds of disco following input")
    parser.add_argument('-f', '--facts', help="Path to python file containing facts (or code to load facts)")
    parser.add_argument('--music', help="Directory containing \"regular\" music")
    parser.add_argument('--special-music', help="Path to python file that loads conditions for special music")
    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = command_line_arguments()
    facts = None
    if args.facts is not None:
        facts_lib = get_loader_lib(args.facts)
        facts = facts_lib.load_facts()
    audio_files = glob.glob('media/general/*')
    CalcApp(facts=facts, disco_length=args.disco_length, audio_src=audio_files, special_music=args.special_music).run()
