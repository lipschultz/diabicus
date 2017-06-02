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
import time

from kivy.core.audio import SoundLoader


class AudioReference:
    STATE_PLAY = 'play'
    STATE_PAUSE = 'pause'
    STATE_STOP = 'stop'
    
    def __init__(self, audio_object, *, start_offset=0, duration=None):
        """
            audio_object is either the Kivy sound object or a string
            representing the path to an audio object
        """
        if isinstance(audio_object, str):
            audio_object = SoundLoader.load(audio_object)

        self.__audio = audio_object
        self.__start = start_offset

        if duration is None:
            duration = audio_object.length - start_offset
        self.__duration = duration

        self.stop()

    @property
    def state(self):
        if self.__audio.state == STATE_PLAY:
            return STATE_PLAY
        elif self.__state == STATE_PLAY:
            self.stop() # do a little housekeeping while we're at it...
            return STATE_STOP
        else:
            return self.__state

    def play(self):
        state = self.state
        if state == STATE_PLAY:
            # already playing...
            pass
        elif state == STATE_STOP or state == STATE_PAUSE:
            self.__audio.play()
            time.sleep(0.1)
            self.__audio.seek(self.__pos)
        self.__state = STATE_PLAY            

    def pause(self):
        self.__pos = self.__audio.get_pos()
        self.__state = STATE_PAUSE
        self.__audio.stop()

    def stop(self):
        self.__pos = self.__start
        self.__state = STATE_STOP
        self.__audio.stop()
