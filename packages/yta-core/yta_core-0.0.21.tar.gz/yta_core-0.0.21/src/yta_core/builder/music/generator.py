"""
This module must be in another library I 
think, like the 'yta-audio' holds the audio
narration generation.
"""
from yta_core.builder.youtube import YoutubeDownloader
from abc import ABC, abstractmethod
from typing import Union


class MusicGenerator(ABC):
    """
    Class to wrap the generation of music for our
    videos.
    """

    @abstractmethod
    def generate(
        keywords: str,
        # TODO: Maybe more parameters
        output_filename: Union[str, None] = None
    ):
        pass

class YoutubeMusicGenerator(MusicGenerator):
    """
    Class that generates music by downloading it from
    our specific Youtube channel.
    """

    def generate(
        keywords: str,
        output_filename: Union[str, None] = None
    ) -> Union[str, None]:
        return YoutubeDownloader().download_music_audio(
            keywords = keywords,
            output_filename = output_filename
        )

# TODO: Here can be Suno AI or any other way
# to generate music

