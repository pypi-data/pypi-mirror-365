"""
These are the options that we allow for the
video generation. If the option is not here,
it is not available.

TODO: Check 'yta-api' project to see a 
broader implementation.
"""
from yta_constants.enum import YTAEnum as Enum


class VoiceNarrationEngine(Enum):
    DEFAULT = 'default'
    """
    When this option is provided, the system will
    choose one of the available enum elements.
    """
    GOOGLE = 'google'

class VoiceNarrationNarratorName(Enum):
    DEFAULT = 'default'
    """
    When this option is provided, the system will
    choose one of the available enum elements.
    """

class VoiceNarrationSpeed(Enum):
    DEFAULT = 'default'
    """
    When this option is provided, the system will
    choose one of the available enum elements.
    """
    NORMAL = 'normal'

class VoiceNarrationEmotion(Enum):
    DEFAULT = 'default'
    """
    When this option is provided, the system will
    choose one of the available enum elements.
    """
    NORMAL = 'normal'

class VoiceNarrationPitch(Enum):
    DEFAULT = 'default'
    """
    When this option is provided, the system will
    choose one of the available enum elements.
    """
    NORMAL = 'normal'