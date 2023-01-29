from .json_dataclass import Element, Field, ListOfElement
from .style import ParagraphStyle, TextStyle
from .layout import Break
from .attr_mixins import Suggested
from .lists import Bullet


class Heading(Element):
    content: str = 'content'
    heading_id: str = Field('headerId', alt_names=('footerId', 'footnoteId'))


class TextRun(Element, Suggested):
    content: str = 'content'
    style: TextStyle = 'textStyle'


class ParagraphElement(Element):
    start: int = Field('startIndex', default=None)
    end: int = 'endIndex'
    text_run: TextRun = 'textRun'
    auto_text: dict = 'autoText'  # todo parse those
    page_break: Break = 'pageBreak'
    column_break: Break = 'columnBreak'
    footnote_ref: dict = 'footnoteReference'
    horizontal_rule: Break = 'horizontalRule'
    equation: dict = 'equation'  # todo parse?
    inline_object_id: str = 'inlineObjectElement.inlineObjectId'
    person: dict = 'person'  # todo parse?
    rich_link: dict = 'richLink'  # google link, todo parse?


class Paragraph(Element, Suggested):
    content: ListOfElement(ParagraphElement) = 'elements'
    positioned_object_ids: ListOfElement(str) = 'positionedObjectIds'
    style: ParagraphStyle = 'paragraphStyle'
    bullet: Bullet = 'bullet'
    positioned: ListOfElement(str) = 'positionedObjectIds'
    """
    Newline terminated content (!)
    """
