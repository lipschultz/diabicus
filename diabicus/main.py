#!/usr/bin/env python3
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

import argparse
import importlib
import glob
import os

from diabicus import calculator
from diabicus import const

def get_file_ext(filename):
    return os.path.splitext(filename)[1]

def get_loader_lib(module_location):
    path, name = os.path.split(module_location)
    module_name = os.path.splitext(name)[0]
    module_path = path
    print('mp:', path, name, module_name, module_path)
    importlib.import_module(module_path)
    return importlib.import_module('.'+module_name, module_path)

def command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disco-length', default=const.DISCO_LENGTH, type=float, help="Number of seconds of disco following input")
    parser.add_argument('-f', '--facts', help="Path to json file with facts")
    parser.add_argument('--music', required=True, nargs='+', help="Path to \"regular\" music (file or directory containing multiple files)")
    parser.add_argument('--special-music', help="Path to json file of tests for special music")
    args = parser.parse_args()
    return args

def main():
    args = command_line_arguments()

    facts = None
    if args.facts is not None:
        from diabicus.cases import youtube_facts
        facts = youtube_facts.YoutubeFact.load_file(args.facts)
    else:
        from diabicus.cases import youtube_facts
        facts = youtube_facts.YoutubeFact.load_file(os.path.join('diabicus', 'data', 'cases', 'facts_youtube.json'))


    special_music = None
    if args.special_music is not None:
        from diabicus.cases import cases, special_music
        special_music = cases.load_json_cases(special_music.SpecialMusicCase, args.special_music)
        

    audio_files = []
    for music_loc in args.music:
        audio_files.extend(glob.glob(music_loc))

    calculator.CalcApp(facts=facts, disco_length=args.disco_length, audio_src=audio_files, special_music=special_music).run()

if __name__=="__main__":
    main()
