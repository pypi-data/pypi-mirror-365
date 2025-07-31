from yta_core.builder import Builder
from yta_core.builder.enums import TextPremade
from yta_core.builder.utils import enum_name_to_class
from yta_core.enums.field import EnhancementField, SegmentField
from yta_validation.parameter import ParameterValidator
from moviepy import VideoFileClip


__all__ = [
    'TextBuilder'
]

class TextBuilder(Builder):
    """
    The builder of the TEXT type.
    """

    @staticmethod
    def build_from_enhancement(
        enhancement: dict
    ) -> VideoFileClip:
        ParameterValidator.validate_mandatory_dict('enhancement', enhancement)

        return TextBuilder.build(
            keywords = enhancement.get(EnhancementField.KEYWORDS.value, None),
            element = enhancement
        )

    @staticmethod
    def build_from_segment(
        segment: dict
    ) -> VideoFileClip:
        ParameterValidator.validate_mandatory_dict('segment', segment)

        return TextBuilder.build(
            keywords = segment.get(SegmentField.KEYWORDS.value, None),
            element = segment
        )
    
    @staticmethod
    def build(
        keywords: str,
        element: dict
    ) -> VideoFileClip:
        """
        For internal use only.
        """
        ParameterValidator.validate_mandatory_string('keywords', keywords, do_accept_empty = False)
        ParameterValidator.validate_mandatory_dict('element', element)

        # Text premades are initialized with the parameters
        # and then the instance sends the parameters to the
        # 'generate' method
        cls = enum_name_to_class(keywords, TextPremade)
        parameters = TextBuilder.get_parameters_from_method(cls.__init__, element)

        # TODO: Maybe 'mask' to set background as transparent if available (?)
        return VideoFileClip(
            cls(**parameters).generate()
        )
        

# TODO: Remove this code below when confirmed that is not used
# def _build_custom_from_text_premade_name(
#     text_premade_name: str,
#     **parameters
# ) -> VideoFileClip:
#     """
#     This method instantiates the 'text_animation_class' Manim
#     text animation class and uses the provided 'parameters' to
#     build the text animation. The provided 'parameters' must 
#     fit the ones requested by the provided class 'generate'
#     method.
#     """
#     ParameterValidator.validate_mandatory_string('text_premade_name', text_premade_name, do_accept_empty = False)

#     # TODO: Maybe 'mask' to set background as transparent if available (?)
#     return VideoFileClip(
#         _text_premade_name_to_class(text_premade_name)().generate(**parameters)
#     )