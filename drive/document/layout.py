from .json_dataclass import Element, ListOfElement
from .style import SpaceStyle, Dimension, TextStyle
from .attr_mixins import Suggested


class SectionColumnProperties(Element):
    padding_end: Dimension = 'paddingEnd'
    width: Dimension = 'width'

    def as_css(self):
        return f"max-width: {self.width.as_css()}; padding-bottom: {self.padding_end.as_css()}"


class SectionStyle(Element, SpaceStyle):
    columns: ListOfElement(SectionColumnProperties) = 'columnProperties'
    separator: str = 'columnSeparatorStyle'  # Enum
    direction: str = 'contentDirection'  # Enum
    section_type: str = 'sectionType'  # ENUM

    def as_css(self):
        """
        Ignored: header, footer, page numberings and header-footer IDs. might be used for anchors later.
        """

        cols = [] if self.columns is None else self.columns
        return f'{self.margins.as_css()};', [q.as_css() for q in cols]


class SectionBreak(Element, Suggested):
    content: SectionStyle = 'sectionStyle'



class Break(Element, Suggested):
    content: TextStyle = 'textStyle'
