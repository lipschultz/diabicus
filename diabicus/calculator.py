#!/usr/bin/python3
# coding=utf-8
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

import cmath
import math
import time
import logging
import glob
import random
from threading import Timer
import webbrowser

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from simpleeval import SimpleEval

from diabicus import compute
from diabicus import const
from diabicus import numeric_tools
from diabicus import time_limit
from diabicus import format_numbers
from diabicus.audio import AudioReference

class CalcMainLayout(BoxLayout):
    pass

class Disco:
    def __init__(self, default_length=const.DISCO_LENGTH):
        self.__stop_time = 0
        self.__default_len = default_length

    def update_stop_time(self, length=None):
        if length is None:
            length = self.__default_len
        self.__stop_time = length + time.time()

    def is_discoing(self):
        return time.time() < self.__stop_time

class Calculator:
    def __init__(self, disco_length=const.DISCO_LENGTH):
        self._result = 0
        self._input = ''
        self._output = ''

        self._num_calculations = 0
        self._num_errors = 0

        self.__eval = SimpleEval()
        self.__init_eval()

        self.__DISPLAY_DIGITS = 7
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
        self.__eval.functions['ln'] = lambda n: math.log(compute.convert_result(n))
        self.__eval.functions['sqrt'] = lambda n: cmath.sqrt(n)
        self.__eval.functions['sin'] = lambda n: math.sin(compute.convert_angle_to_radian(compute.convert_result(n), self.is_radians))
        self.__eval.functions['cos'] = lambda n: math.cos(compute.convert_angle_to_radian(compute.convert_result(n), self.is_radians))
        self.__eval.functions['tan'] = lambda n: math.tan(compute.convert_angle_to_radian(compute.convert_result(n), self.is_radians))

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
        if len(self.input) == 0 and value in ('×', '/', '^', '×10^'):
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
            self._num_errors += 1
        else:
            self.result = result
            self.output = result
            self._num_calculations += 1
        self.__just_calculated = True
        logging.info('Calculator.calculate: output = '+str(self.output))
        self.context['result'].append(result)
        self.context['formula'].append(self.input)
        self.context['output'].append(self.output)
        return result

class CalcApp(App, Calculator):
    def __init__(self, *args, **kwargs):
        self.__facts = kwargs.pop('facts', None)
        self.__fact_current = None

        self.__audio = kwargs.pop('audio_src', [])
        self.__audio_current = None

        self.__special_music = kwargs.pop('special_music', None)
        self.__special_music_current = None

        super(CalcApp, self).__init__(*args, **kwargs)

        self._answer_format = {complex : lambda v: format_numbers.pretty_print_complex(format_numbers.simplify_complex(v), lambda n: format_numbers.to_pretty_x10(n, 2)),#lambda v : '%0.1g + %0.2gi' % (v.real, v.imag),
                               float : lambda v : "%0.4g" % v
                               }
        self._answer_format[int] = self._answer_format[float]

        self.timed_exec = time_limit.TimedExecution()

        calc_display_thread = Timer(0.75, self.set_num_calculations_display)
        calc_display_thread.daemon = True
        calc_display_thread.start()

        self.__flashable_button_defaults = None

    def __init_eval(self):
        super(CalcApp, self).__init_eval()
        del self.__eval.names['True']
        del self.__eval.names['False']

    def build(self):
        return CalcMainLayout()

    def toggle_angle(self):
        if self.root.ids.top_border.ids.angle_units.state == 'down':
            self.root.ids.top_border.ids.angle_units.text = '[s] Degrees [/s]\n[b]Radians[/b]'
        else:
            self.root.ids.top_border.ids.angle_units.text = '[b]Degrees[/b]\n[s] Radians [/s]'

    def is_radians(self):
        return self.root.ids.top_border.ids.angle_units.state == 'down'

    def open_fact(self):
        if self.__fact_current is not None and self.__fact_current.link is not None:
            webbrowser.open(self.__fact_current.link)

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

    def set_music_display(self, value):
        if value == '' or value is None:
            self.root.ids.music_display.text = ''
        else:
            self.root.ids.music_display.text = 'Audio: ' + value

    def set_num_calculations_display(self):
        output = '# Calculations: ' + str(self._num_calculations)
        if self._num_errors > 0:
            output += ', # Errors: ' + str(self._num_errors)
        self.root.ids.num_calculations.text = output

    def __set_clear_button(self, to_all_clear=False):
        pass

    def __is_special_music_playing(self):
        return self.__special_music_current is not None and self.__special_music_current.state == AudioReference.STATE_PLAY

    def __stop_special_music(self):
        if self.__special_music_current is not None:
            self.__special_music_current.stop()

    def __play_new_audio(self):
        choice = random.choice(self.__audio)
        self.__audio_current = AudioReference(choice)
        self.__audio_current.play()
        self.set_music_display(self.__audio_current.display_name)

    def update_disco(self, dt):
        do_play = super(CalcApp, self).update_disco(dt)
        if not self.__is_special_music_playing():
            if do_play:
                if self.__audio_current is None or self.__audio_current.state == AudioReference.STATE_STOP:
                    self.__play_new_audio()
                else:
                    self.__audio_current.play()
                    self.set_music_display(self.__audio_current.display_name)
                self.__shine_lights()
            else:
                self.__pause_disco()
                self.set_music_display('')
        else:
            self.__shine_lights()

    def __pause_disco(self):
        if self.__audio_current is not None and self.__audio_current.state == 'play':
            self.__audio_current.pause()
        self.__reset_lights()

    def __get_border_lights(self):
        lights = []
        for container in (self.root.ids.right_side, self.root.ids.left_side, self.root.ids.top_border, self.root.ids.bottom_border):
            lights.extend([container.ids.get(ref) for ref in container.ids.keys() if 'light' in ref])
        return lights

    def __get_flashable_buttons(self):
        buttons = []
        for container in (self.root.ids.right_side, self.root.ids.left_side, self.root.ids.top_border, self.root.ids.bottom_border):
            buttons.extend([container.ids.get(ref) for ref in container.ids.keys() if 'light' not in ref])

        if self.__flashable_button_defaults is None:
            self.__flashable_button_defaults = {}
            for b in buttons:
                self.__flashable_button_defaults[b] = (b.background_normal, b.background_down)

        return buttons

    def __shine_lights(self):
        shining_images = glob.glob('diabicus/data/images/*_shining.png')

        lights = self.__get_border_lights()
        for l in lights:
            l.source = random.choice(shining_images)

        buttons = self.__get_flashable_buttons()
        for b in buttons:
            choice = random.choice(shining_images)
            b.background_normal = choice
            b.background_down = choice

    def __reset_lights(self):
        lights = self.__get_border_lights()
        for l in lights:
            l.source = 'diabicus/data/images/light_grey_off.png'

        if self.__flashable_button_defaults is not None:
            buttons = self.__get_flashable_buttons()
            for b in buttons:
                b.background_normal = self.__flashable_button_defaults[b][0]
                b.background_down = self.__flashable_button_defaults[b][1]

    def calculate(self):
        self.__get_border_lights()
        result = super(CalcApp, self).calculate()
        self.set_num_calculations_display()
        if self.__facts is not None:
            fact = self.__fact_current = self.__facts.get_case(self.input, result, self.context)
            if fact is not None:
                message = fact.title
                try:
                    message = self.timed_exec.run(fact.message, self.input, result, self.context)
                except TimeoutError as e:
                    logging.warn('CalcApp.calculate: Getting message timed out for fact '+str(fact))

                self.root.ids.fact.text = message
        if self.__special_music is not None:
            smusic = self.__special_music.get_case(self.input, result, self.context)
            if smusic is not None:
                self.__pause_disco()
                self.__stop_special_music()
                self.__special_music_current = AudioReference(smusic.filename, start_offset=smusic.start, duration=smusic.duration, end_time=smusic.end)
                self.__special_music_current.play()
                self.set_music_display(smusic.cite)
