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

    def as_html(self, root):
        if self.style.link is not None:
            return f'<a href="{self.style.link.url} style="{self.style.as_css(root)}">{self.content}</a>'
        return f'<span style="{self.style.as_css(root)}">{self.content}</span>'


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

    def as_html(self, root):
        if self.horizontal_rule is not None:
            return '<hr>'
        if self.inline_object_id is not None:
            return root.inline_objects.get(self.inline_object_id).as_html(root)
        return f'{"" if self.text_run is None else self.text_run.as_html(root)}'


class Paragraph(Element, Suggested):
    content: ListOfElement(ParagraphElement) = 'elements'
    style: ParagraphStyle = 'paragraphStyle'
    bullet: Bullet = 'bullet'
    positioned: list = 'positionedObjectIds'
    """
    Newline terminated content (!)
    """

    def as_html(self, root):
        data = "".join([q.as_html(root) for q in self.content])
        tag = 'p'
        if self.style.named_style is not None:
            style = next((q for q in root.named_styles if q.style_type == self.style.named_style), None)
            if style is not None:
                base_style = style.paragraph_as_css(root)
                if 'HEADING' in self.style.named_style:
                    tag = f'h{int(self.style.named_style[-1])+2}'
                if self.style.named_style == 'TITLE':
                    tag = 'h1'
                if self.style.named_style == 'SUBTITLE':
                    tag = 'h2'
        else:
            base_style = self.style.as_css(root)
        return f'<{tag} style="{base_style}">{data}</{tag}>'
