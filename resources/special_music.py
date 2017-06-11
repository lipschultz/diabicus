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

import os

from src import cases
from src.numeric_tools import *

class SpecialMusicCase:
    """
    Class to hold a specific case for playing special music.
    """
    def __init__(self, json_data):
        self.json_data = json_data
        self.raw_test = json_data.get('test')
        self.filename = json_data.get('file')
        self.link = json_data.get('link')
        self.cite = json_data.get('cite')
        self.start = json_data.get('start', 0)
        self.end = json_data.get('end')
        self.duration = json_data.get('duration')
        self.weight = json_data.get('weight', 1)

        try:
            self.test = eval(self.raw_test)
        except Exception:
            self.test = False
        if not callable(self.test):
            self.test = lambda *args: False
        
        if self.cite is None:
            if self.link is not None:
                self.cite = self.link
            else:
                self.cite = self.filename
        
        #if self.duration < 0 or not os.path.exists(self.filename):
        #    self.test = lambda *args: False

    def __str__(self):
        return self.cite

    def __repr__(self):
        return str(self) + "{test : " + repr(self.raw_test.encode("unicode-escape")) + "}"

def load():
    path = os.path.dirname(__file__)
    return cases.load_json_cases(SpecialMusicCase, os.path.join(path, 'special_music.json'))

