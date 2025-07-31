"""
Conditions that are mandatory according to the 
component configuration. These conditions, if
applicable, will raise an exception if not met.
"""
from yta_core.enums.field import _Field, MusicField, VoiceNarrationField
from yta_validation.parameter import ParameterValidator
from abc import ABC, abstractmethod


class MandatoryCondition(ABC):
    """
    Class to representa a component configuration 
    mandatory condition that will raise an Exception
    if not met or will be applied if met.
    """

    @staticmethod
    @abstractmethod
    def is_satisfied(
        component: dict
    ):
        pass

class DoNeedKeywords(MandatoryCondition):
    """
    Check if the 'do_need_keywords' mandatory condition
    is satisfied or not.
    """

    _attribute: str = 'do_need_keywords'

    @staticmethod
    def is_satisfied(
        component: dict
    ) -> bool:
        """
        Check if the 'do_need_keywords' mandatory condition
        is satisfied or not.
        """
        ParameterValidator.validate_mandatory_dict('component', component)

        return component.get(_Field.KEYWORDS.value, None)
    
class DoNeedFilenameOrUrl(MandatoryCondition):
    """
    Check if the 'do_need_filename_or_url' mandatory
    condition is satisfied or not.
    """

    _attribute: str = 'do_need_filename_or_url'

    @staticmethod
    def is_satisfied(
        component: dict
    ) -> bool:
        """
        Check if the 'do_need_filename_or_url' mandatory
        condition is satisfied or not.
        """
        ParameterValidator.validate_mandatory_dict('component', component)

        # TODO: Should this be different from '' (?)
        return (
            component.get(_Field.FILENAME.value, None) or
            component.get(_Field.URL.value, None) 
        )
    
class DoNeedText(MandatoryCondition):
    """
    Check if the 'do_need_text' mandatory
    condition is satisfied or not.
    """

    _attribute: str = 'do_need_text'

    @staticmethod
    def is_satisfied(
        component: dict
    ) -> bool:
        """
        Check if the 'do_need_text' mandatory
        condition is satisfied or not.
        """
        ParameterValidator.validate_mandatory_dict('component', component)

        # TODO: Should this be different from '' (?)
        return component.get(_Field.TEXT.value, None) 
    
class DoNeedSpecificDuration(MandatoryCondition):
    """
    Check if the 'do_need_specific_duration' mandatory
    condition is satisfied or not.
    """

    _attribute: str = 'do_need_specific_duration'

    @staticmethod
    def is_satisfied(
        component: dict
    ) -> bool:
        """
        Check if the 'do_need_specific_duration' mandatory
        condition is satisfied or not.
        """
        ParameterValidator.validate_mandatory_dict('component', component)

        return (
            component.get(_Field.DURATION.value, None) or
            DoNeedNarration.is_satisfied(component)
        )
    
class DoNeedNarration(MandatoryCondition):
    """
    Check if the 'do_need_narration' mandatory
    condition is satisfied or not.
    """

    _attribute: str = 'do_need_narration'

    @staticmethod
    def is_satisfied(
        component: dict
    ) -> bool:
        """
        Check if the 'do_need_narration' mandatory
        condition is satisfied or not.
        """
        ParameterValidator.validate_mandatory_dict('component', component)

        voice_narration: dict = component.get(_Field.VOICE_NARRATION.value, None)

        return (
            # TODO: Maybe check if 'voice_narration' is dict
            voice_narration and
            # Filename will be used directly
            voice_narration.get(VoiceNarrationField.FILENAME.value, None) or
            (
                # We need all this to be able to narrate, they can
                # provide 'default' values for many of the fields
                # if they don't want to choose
                voice_narration.get(VoiceNarrationField.TEXT.value, None) and
                voice_narration.get(VoiceNarrationField.ENGINE.value, None) and
                voice_narration.get(VoiceNarrationField.LANGUAGE.value, None) and
                voice_narration.get(VoiceNarrationField.NARRATOR_NAME.value, None) and
                voice_narration.get(VoiceNarrationField.SPEED.value, None) and
                voice_narration.get(VoiceNarrationField.EMOTION.value, None) and
                voice_narration.get(VoiceNarrationField.PITCH.value, None)
            )
        )
    
class DoNeedMusic(MandatoryCondition):
    """
    Check if the 'do_need_music' mandatory
    condition is satisfied or not.
    """

    _attribute: str = 'do_need_music'

    @staticmethod
    def is_satisfied(
        component: dict
    ) -> bool:
        """
        Check if the 'do_need_music' mandatory
        condition is satisfied or not.
        """
        ParameterValidator.validate_mandatory_dict('component', component)

        music: dict = component.get(_Field.MUSIC.value, None)

        return (
            music and
            # Filename will be used directly
            music.get(MusicField.FILENAME.value, None) or
            music.get(MusicField.URL.value, None) or
            (
                music.get(MusicField.ENGINE.value, None) and
                music.get(MusicField.KEYWORDS.value, None)
            )
        )
