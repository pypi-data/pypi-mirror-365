from yta_core.builder import Builder
from yta_core.enums.field import EnhancementField, SegmentField
from yta_validation.parameter import ParameterValidator
from moviepy import VideoFileClip
from typing import Union


__all__ = [
    'AIVideoBuilder'
]

class AIVideoBuilder(Builder):
    """
    The builder of the AI_VIDEO type.

    TODO: This has not been implemented yet.
    """

    @staticmethod
    def build_from_enhancement(
        enhancement: dict
    ):
        """
        Build the video content from the information
        in the given 'enhancement' dict.
        """
        ParameterValidator.validate_mandatory_dict('enhancement', enhancement)

        return AIVideoBuilder._build(
            keywords = enhancement.get(EnhancementField.KEYWORDS.value, None),
            duration = enhancement.get(EnhancementField.DURATION.value, None)
        )

    @staticmethod
    def build_from_segment(
        segment: dict
    ):
        """
        Build the video content from the information
        in the given 'segment' dict.
        """
        ParameterValidator.validate_mandatory_dict('segment', segment)

        return AIVideoBuilder._build(
            keywords = segment.get(SegmentField.KEYWORDS.value, None),
            duration = segment.get(SegmentField.DURATION.value, None)
        )
    
    @staticmethod
    def _build(
        keywords: str,
        duration: Union[float, int]
    ) -> VideoFileClip:
        """
        Build the video content with the given 'keywords'
        and 'duration'.
        """
        # TODO: By now we are processing it as an AIImage
        from yta_core.builder.ai_image_builder import AIImageBuilder

        return AIImageBuilder.build(
            keywords = keywords,
            duration = duration
        )
        raise Exception('This functionality has not been implemented yet.')
        # TODO: Check how AIImageBuilder works with the
        # AIImage @dataclass and imitate it
        return VideoFileClip('test.mp4')
