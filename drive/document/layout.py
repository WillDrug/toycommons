from .json_dataclass import Element
from .style import SpaceStyle, Dimension, TextStyle
from .attr_mixins import Suggested


class SectionStyle(Element, SpaceStyle):
    width: Dimension = 'columnProperties.width'
    padding_end: Dimension = 'columnProperties.paddingEnd'
    separator: str = 'columnSeparatorStyle'  # Enum
    direction: str = 'contentDirection'  # Enum
    section_type: str = 'sectionType'  # ENUM


class SectionBreak(Element, Suggested):
    content: SectionStyle = 'sectionStyle'

    def as_html(self, root):
        return ''  # fixme: use as <div>?


class Break(Element, Suggested):
    content: TextStyle = 'textStyle'
