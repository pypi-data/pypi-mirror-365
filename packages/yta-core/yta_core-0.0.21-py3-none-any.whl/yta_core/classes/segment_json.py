"""
TODO: Maybe I need to move this class to another
module if I'm not sure that it fits well here
"""
from yta_core.classes.enhancement_json import EnhancementJson
from yta_core.classes.music_json import MusicJson
from yta_core.classes.voice_narration_json import VoiceNarrationJson
from dataclasses import dataclass
from typing import Union

import json


@dataclass
class SegmentJson:
    """
    @dataclass
    The information a Segment must hold. This
    information is about a segment that is being
    processed, so its values can be different
    from the original json because they have 
    been processed.
    """

    type: str
    url: str
    text: str
    keywords: list[str]
    filename: str
    voice_narration: Union[VoiceNarrationJson, None]
    music: Union[MusicJson, None]

    enhancements: list[EnhancementJson]
    extra_params: dict
    duration: float
    status: str
    created_at: str

    def __init__(self):
        """
        Initializes the instance with empty string
        values for all the attributes so we can
        fill them later and individually when
        processing.
        """
        self.type = ''
        self.url = ''
        self.text = ''
        self.keywords = []
        self.filename = ''
        self.voice_narration = None
        self.music = None
        self.enhancements = []
        self.extra_params = {}
        self.duration = 0.0
        self.status = ''
        self.created_at = ''

    @property
    def as_dict(self):
        """
        Get the instance as a dictionary.
        """
        return {
            'type': self.type,
            'url': self.url,
            'text': self.text,
            'keywords': self.keywords,
            'filename': self.filename,
            'voice_narration': (
                self.voice_narration.as_dict
                if self.voice_narration is not None else
                None
            ),
            'music': (
                self.music.as_dict
                if self.music is not None else
                None
            ),
            'enhancements': [
                enhancement.as_dict
                for enhancement in self.enhancements
            ],
            'extra_params': self.extra_params,
            'duration': self.duration,
            'status': self.status,
            'created_at': self.created_at
        }

    @property
    def as_json(self):
        """
        Get the instance as a json, transformed
        from the dictionary version.
        """
        return json.dumps(self.as_dict)