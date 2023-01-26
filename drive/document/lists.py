from .json_dataclass import Element, ListOfElement, Field
from .attr_mixins import Suggested
from .style import TextStyle, Dimension


class Bullet(Element):
    list_id: str = 'listId'
    nesting_level: int = 'nestingLevel'
    text_style: TextStyle = 'textStyle'


class NestingLevel(Element):
    bullet_alignment: str = 'bulletAlignment'  # enum
    glyph_format: str = 'glyphFormat'
    indent_first_line: Dimension = 'indentFirstLine'
    indent_start: Dimension = 'indentStart'
    text_style: TextStyle = 'textStyle'
    start_number: int = 'startNumber'
    glyph: str = Field('glyphType', alt_names=('glyphSymbol',))  # enum or the character itself (!)


class List(Element, Suggested):
    nesting_levels: ListOfElement(NestingLevel) = 'listProperties.nestingLevels'
