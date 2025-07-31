from yta_constants.enum import YTAEnum as Enum
from yta_text.finder import TextFinderOption as EditionManualTermOption


__all__ = [
    'EditionManualTermContext',
    'EditionManualTermField',
    'EditionManualTermOption'
]

class EditionManualTermContext(Enum):
    """
    This is the context our edition terms will have.
    The context will determine in which text topics
    we will need to apply the edition term.
    """
    
    ANY = 'any'
    """
    The term will be applied always, in any context.
    """
    
    @classmethod
    def get_default(
        cls
    ):
        """
        Get the item by default.
        """
        return cls.ANY

class EditionManualTermField(Enum):
    """
    Enum class to wrap the different fields an
    edition manual term can have.
    """

    OPTIONS = 'options'
    """
    The options we need to use when searching
    for the edition manual term to match the
    text. Check the option in the TextFinder
    class (from 'yta_text' library).
    """
    CONTEXT = 'context'
    """
    The context in which the the edition manual
    term should be applied, that could be a
    a topic, a category, etc.
    """
    ENHANCEMENTS = 'enhancements'
    """
    The content enhancements that must be 
    applied when this eidion manual term has
    to.
    """