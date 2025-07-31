from yta_core.builder.voice_narration.enums import VoiceNarrationEmotion,VoiceNarrationEngine, VoiceNarrationSpeed, VoiceNarrationNarratorName
from yta_core.enums.field_v2 import _Field
from yta_core.validation import VoiceNarrationField, VoiceNarrationEmotionField, VoiceNarrationEngineField, VoiceNarrationLanguageField, VoiceNarrationFilenameField, VoiceNarrationNarratorNameField, VoiceNarrationSpeedField, VoiceNarrationTextField
from yta_shortcodes.parser import ShortcodeParser
from yta_audio_narration.narrator import GoogleVoiceNarrator
from yta_validation.parameter import ParameterValidator
from typing import Union


class VoiceNarrationConcept:
    """
    Class to simplify the way we handle the 
    'voice_narration' for a component.

    This class must be used when the component json
    structure has been validated and it is ready for
    the building process.

    TODO: Check 'validation.py' for the validation
    process.
    """

    @staticmethod
    def do_should_be_handled(
        element: dict
    ) -> bool:
        """
        Check if the 'voice_narration' should be handled
        or not according to the parameters set in the
        given 'element'.

        The 'element' must be a dictionary previously
        validated so we know it has the mandatory 
        strcture.
        """
        return element.get(_Field.VOICE_NARRATION, None) is not None
    
    @staticmethod
    def validate(
        element: dict
    ):
        """
        Validate that the 'voice_narration' fields are
        set and valid for loading a voice narration from
        a file or for generating a new one.

        The 'element' must be a dictionary previously
        validated so we know it has the mandatory 
        structure.
        """
        voice_narration = element.get(_Field.VOICE_NARRATION.value, None)

        if voice_narration is not None:
            # Validate all fields are, at least, set
            ParameterValidator.validate_dict_has_keys('voice_narration', voice_narration, VoiceNarrationField.get_all_values())

            filename = voice_narration[VoiceNarrationField.FILENAME.value]
            text = voice_narration[VoiceNarrationField.TEXT.value]
            engine = voice_narration[VoiceNarrationField.ENGINE.value]
            language = voice_narration[VoiceNarrationField.LANGUAGE.value]
            narrator_name = voice_narration[VoiceNarrationField.NARRATOR_NAME.value]
            speed = voice_narration[VoiceNarrationField.SPEED.value]
            emotion = voice_narration[VoiceNarrationField.EMOTION.value]

            # Validate the combination of fields values are valid
            if (
                filename is not None and
                not VoiceNarrationFilenameField(filename).is_valid
            ):
                raise Exception('The provided "voice_narration" "filename" field is not a valid audio file.')

            if (
                filename is None and
                (
                    not VoiceNarrationTextField(text).is_valid or
                    not VoiceNarrationEngineField(engine).is_valid or
                    not VoiceNarrationLanguageField(language, engine).is_valid or
                    not VoiceNarrationNarratorNameField(narrator_name).is_valid or
                    not VoiceNarrationSpeedField(speed).is_valid or
                    not VoiceNarrationEmotionField(emotion).is_valid
                )
            ):
                raise Exception('At least one of the "voice_narration" parameters needed is not valid.')
            
    @staticmethod
    def get(
        voice_narration: dict,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Obtain the voice narration, store it locally 
        and return the filename string. The provided
        'voice_narration' parameter must be the dict
        within the component dict.
        """
        filename = voice_narration[VoiceNarrationField.FILENAME.value]

        # TODO: 'text' has to be sanitized before using
        if not voice_narration['text_sanitized']:
            parser = ShortcodeParser()
            parser.parse(voice_narration[VoiceNarrationField.TEXT.value])
            text = parser.text_sanitized_without_shortcodes
        else:
            text = voice_narration['text_sanitized']

        return (
            filename
            if filename is not None else
            VoiceNarrationConcept._generate(
                text = text,
                engine = voice_narration[VoiceNarrationField.ENGINE.value],
                narrator_name = voice_narration[VoiceNarrationField.NARRATOR_NAME.value],
                speed = voice_narration[VoiceNarrationField.SPEED.value],
                emotion = voice_narration[VoiceNarrationField.EMOTION.value],
                output_filename = output_filename
            )
        )

    @staticmethod
    def _generate(
        text: str,
        engine: VoiceNarrationEngine,
        narrator_name: VoiceNarrationNarratorName,
        speed: VoiceNarrationSpeed,
        emotion: VoiceNarrationEmotion,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Generate a voice narration with the given 'text'
        and parameters, and stores it locally with the
        given 'output_filename'.
        """
        engine = VoiceNarrationEngine.to_enum(engine)
        narrator_name = VoiceNarrationNarratorName.to_enum(narrator_name)
        speed = VoiceNarrationSpeed.to_enum(speed)
        emotion = VoiceNarrationEmotion.to_enum(emotion)

        # TODO: How to actually handle these 'speed' and
        # 'emotion' according to the 'engine' chosen (?)

        # TODO: Handle params, please
        return GoogleVoiceNarrator.narrate(
            text = text,
            output_filename = output_filename
        )
    
# TODO: Check yta-api because I'm validating it there