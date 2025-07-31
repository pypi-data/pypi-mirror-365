"""
This is a complex parameter which includes
different attributes to make possible the
music construction.

This parameter can be None if no music is
requested, or can have different values
according to the expected way of building
it.
"""
from yta_core.builder.music.enums import MusicEngine
from dataclasses import dataclass
from typing import Union

import json


@dataclass
class MusicJson:
    """
    @dataclass
    The information the Music parameter must hold.
    This information is about a music that is going
    to be added in a video.
    """

    filename: str
    url: str
    engine: Union[MusicEngine, None]
    keywords: str
    filename_processed: str
    """
    The filename that has been built and/or processed
    and is able to be used for the Segment or 
    Enhancement.
    """

    def __init__(self):
        """
        Initializes the instance with empty string
        values for all the attributes so we can
        fill them later and individually when
        processing.
        """
        self.filename = ''
        self.url = ''
        self.engine = None
        self.keywords = ''
        self.filename_processed = ''

    @property
    def as_dict(self):
        """
        Get the instance as a dictionary.
        """
        return {
            'filename': self.filename,
            'url': self.url,
            'engine': (
                self.engine.value
                if self.engine is not None else
                None
            ),
            'keywords': self.keywords,
            'filename_processed': self.filename_processed
        }

    @property
    def as_json(self):
        """
        Get the instance as a json, transformed
        from the dictionary version.
        """
        return json.dumps(self.as_dict)