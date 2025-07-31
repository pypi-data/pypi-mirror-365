"""
This is a complex parameter which includes
different attributes to make possible the
voice narration construction.

This parameter can be None if no voice
narration is requested, or can have different
values according to the expected way of
building it.
"""
from yta_audio_narration_common.enums import VoiceEmotion, VoicePitch, VoiceSpeed, NarrationLanguage
from yta_audio_narration.enums import VoiceNarrationEngine
from dataclasses import dataclass
from typing import Union

import json


@dataclass
class VoiceNarrationJson:
    """
    @dataclass
    The information the Music parameter must hold.
    This information is about a music that is going
    to be added in a video.
    """

    filename: str
    text: str
    engine: Union[VoiceNarrationEngine, None]
    language: Union[NarrationLanguage, None]
    # Narrator names are specific for each engine,
    # we don't have a common Enum
    narrator_name: Union[str, None]
    speed: Union[VoiceSpeed, None]
    emotion: Union[VoiceEmotion, None]
    pitch: Union[VoicePitch, None]
    text_sanitized: str
    """
    The text but sanitized, which means that any
    unexpected mark, accent, double space or 
    whatever makes the narration malfunction has
    been removed.
    """
    text_sanitized_without_shortcodes: str
    text_with_simplified_shortcodes: str

    def __init__(self):
        """
        Initializes the instance with empty string
        values for all the attributes so we can
        fill them later and individually when
        processing.
        """
        self.filename = ''
        self.text = ''
        self.engine = None
        self.language = None
        self.narrator_name = None
        self.speed = None
        self.emotion = None
        self.pitch = None
        # TODO: I need the sanitized without shortcodes,
        # but what about the other ones? are needed here (?)
        self.text_sanitized = ''
        self.text_sanitized_without_shortcodes = ''
        self.text_with_simplified_shortcodes = ''

    @property
    def as_dict(self):
        """
        Get the instance as a dictionary.
        """
        return {
            'filename': self.filename,
            'text': self.text,
            'engine': (
                self.engine.value
                if self.engine is not None else
                None
            ),
            'language': {
                self.language.value
                if self.language is not None else
                None
            },
            # 'narrator_name': (
            #     self.narrator_name.value
            #     if self.narrator_name is not None else
            #     None
            # ),
            # Narrator name is different for each engine
            # so we don't have a common Enum
            'narrator_name': self.narrator_name,
            'speed': (
                self.speed.value
                if self.speed is not None else
                None
            ),
            'emotion': (
                self.emotion.value
                if self.emotion is not None else
                None
            ),
            'pitch': {
                self.pitch.value
                if self.pitch is not None else
                None
            },
            'text_sanitized': self.text_sanitized,
            'text_sanitized_without_shortcodes': self.text_sanitized_without_shortcodes,
            'text_with_simplified_shortcodes': self.text_with_simplified_shortcodes
        }

    @property
    def as_json(self):
        """
        Get the instance as a json, transformed
        from the dictionary version.
        """
        return json.dumps(self.as_dict)