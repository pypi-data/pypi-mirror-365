from yta_core.enums.field_v2 import _Field, MusicField
from yta_core.validation import MusicEngineField, MusicFilenameField, MusicKeywordsField, MusicUrlField
from yta_core.builder.music.enums import MusicEngine
from yta_core.builder.music.generator import YoutubeMusicGenerator
from yta_file.handler import FileHandler
from yta_file_downloader import Downloader
from yta_validation.parameter import ParameterValidator
from typing import Union


class MusicConcept:
    """
    Class to simplify the way we handle the 'music'
    for a component.

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
        Check if the 'music' should be handled or not according
        to the parameters set in the given 'element'.
        """
        return element.get(_Field.MUSIC, None) is not None
    
    @staticmethod
    def validate(
        element: dict
    ):
        """
        Validate that the 'music' fields are set and
        valid for loading music from a file or for
        obtaining or creating the expected music.
        """
        music = element.get(_Field.MUSIC.value, None)

        if music is not None:
            # Validate all fields are, at least, set
            ParameterValidator.validate_dict_has_keys('music', music, MusicField.get_all_values())

            filename = music[MusicField.FILENAME.value]
            url = music[MusicField.URL.value]
            engine = music[MusicField.ENGINE.value]
            keywords = music[MusicField.KEYWORDS.value]

            # Validate the combination of fields values are valid
            if (
                filename is not None and
                not MusicFilenameField(filename).is_valid
            ):
                raise Exception('The provided "music" "filename" field is not a valid audio file.')

            if (
                filename is None and
                (
                    not MusicFilenameField(filename).is_valid or
                    not MusicUrlField(url).is_valid or
                    not MusicEngineField(engine).is_valid or
                    not MusicKeywordsField(keywords).is_valid
                )
            ):
                raise Exception('At least one of the "music" parameters needed is not valid.')
            
    @staticmethod
    def get(
        music: dict
    ) -> str:
        """
        Obtain the music, store it locally and return
        the filename string. The provided 'music'
        parameter must be the dict within the component
        dict.
        """
        filename = music[MusicField.FILENAME.value]
        url = music[MusicField.URL.value]
        keywords = music[MusicField.KEYWORDS.value]
        engine = music[MusicField.ENGINE.value]

        if filename is not None:
            music_filename = filename
            if not FileHandler.is_audio_file(music_filename):
                raise Exception('The provided "filename" is not an audio file.')
        elif url is not None:
            music_filename = Downloader.download_audio(url)
            # TODO: What about this? Should be done in advance
            # when the parameters are provided? It can be available
            # when provided but not when the video is actually being
            # generated...
            if not FileHandler.is_audio_file(music_filename):
                raise Exception('The provided "url" is not an audio file.')
        elif keywords is not None:
            music_filename = MusicConcept._generate(
                kewords = keywords,
                engine = MusicEngine.to_enum(engine)
            )

        return music_filename
            
    @staticmethod
    def _generate(
        keywords: str,
        engine: MusicEngine,
        output_filename: Union[str, None] = None
    ) -> Union[str, None]:
        ParameterValidator.validate_mandatory_string('keywords', keywords, do_accept_empty = False)
        engine = MusicEngine.to_enum(engine)

        # TODO: What if we make a method to turn 'DEFAULT'
        # option into another one (?)
        engine = (
            MusicEngine.YOUTUBE
            if engine == MusicEngine.DEFAULT else
            engine
        )

        return {
            MusicEngine.YOUTUBE: lambda keywords, output_filename: YoutubeMusicGenerator.generate(
                keywords = keywords,
                output_filename = output_filename
            )
        }[engine](keywords, output_filename)
        
    

    
