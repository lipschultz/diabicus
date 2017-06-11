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
from threading import Timer

from kivy.core.audio import SoundLoader

import mutagen


class AudioReference:
    STATE_PLAY = 'play'
    STATE_PAUSE = 'pause'
    STATE_STOP = 'stop'
    
    def __init__(self, audio_filename, *, start_offset=0, duration=None, end_time=None):
        """
            Either `duration` or `end_time` should be specified.  If both are, then
            `end_time`'s value will be used.
        """
        self.__filename = audio_filename
        self.__audio = SoundLoader.load(audio_filename)
        self.__metadata = mutagen.File(audio_filename) or {}
        self.__start = start_offset

        self.__audio.length # Kivy won't play the audio without this...

        if end_time is not None:
            self.__end_time = end_time
        elif duration is not None:
            self.__end_time = self.__start + duration
        else:
            self.__end_time = None

        self.__stop_thread = None

        self.stop()

    @property
    def filename(self):
        return self.__filename

    @property
    def state(self):
        if self.__audio.state == self.STATE_PLAY:
            return self.STATE_PLAY
        elif self.__state == self.STATE_PLAY:
            self.stop() # do a little housekeeping while we're at it...
            return self.STATE_STOP
        else:
            return self.__state

    @property
    def display_name(self):
        artist = self.artist
        title = self.title
        if artist is None or title is None:
            return self.filename
        else:
            return artist + ' - ' + title

    @property
    def artist(self):
        return self.get_tag({'TPE1' : lambda v: v.text[0],
                             'ARTIST' : None
                             })

    @property
    def title(self):
        return self.get_tag({'TIT2' : lambda v: v.text[0],
                             'TITLE' : None
                             })

    def get_tag(self, tag_transforms):
        for tag, transform in tag_transforms.items():
            value = self.__metadata.get(tag)
            if value is not None:
                if transform is None:
                    return value[0]
                else:
                    return transform(value)

    def play(self):
        state = self.state
        if state == self.STATE_PLAY:
            # already playing...
            pass
        elif state == self.STATE_STOP or state == self.STATE_PAUSE:
            self.__audio.play()
            time.sleep(0.1)
            self.__audio.seek(self.__pos)

            if self.__end_time is not None:
                duration = self.__end_time - self.__pos
                self.__stop_thread = Timer(duration, self.stop)
                self.__stop_thread.daemon = True
                self.__stop_thread.start()
        self.__state = self.STATE_PLAY

    def pause(self):
        self.__pos = self.__audio.get_pos()
        self.__state = self.STATE_PAUSE
        self.__audio.stop()

    def stop(self):
        self.__pos = self.__start
        self.__state = self.STATE_STOP
        self.__audio.stop()

        if self.__stop_thread is not None:
            self.__stop_thread.cancel()
            self.__stop_thread = None
