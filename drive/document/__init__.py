from typing import Union
from .json_dataclass.element import Element, DictOfElement, ListOfElement, Field
from .tables import Table
from .style import DocumentStyle, NamedStyle
from .ranges import NamedRange
from .objects import InlineOrPositionedObject
from .lists import List
from .paragraph import Paragraph, Heading
from .table_of_contents import TableOfContents
from .layout import SectionBreak


class StructuralElement(Element):
    start: int = Field('startIndex', default=0)
    end: int = 'endIndex'  # detection: elements, sectionStyle, tableRows, content
    content: Union[Paragraph, SectionBreak, Table, TableOfContents] = Field('paragraph',
                                                                            alt_names=('sectionBreak',
                                                                                       'table',
                                                                                       'tableOfContents'),
                                                                            strict=True
                                                                            )

    def _content(self, value: dict):
        # guessing game GO! fixme: You can create a GuessType type for this.
        if 'elements' in value:
            return Paragraph(value)
        elif 'sectionStyle' in value:
            return SectionBreak(value)
        elif 'tableRows' in value:
            return Table(value)
        elif 'content' in value:
            return TableOfContents(value)
        else:
            return None

    def as_html(self, root):
        return self.content.as_html(root)


class GoogleDoc(Element):
    title: str = 'title'
    doc_id: str = 'document_id'
    body: ListOfElement(StructuralElement) = 'body.content'
    headers: DictOfElement(Heading) = 'headers'
    footers: DictOfElement(Heading) = 'footers'
    footnotes: DictOfElement(Heading) = 'footnotes'
    style: DocumentStyle = 'documentStyle'
    suggested_style = 'suggestedDocumentStyleChanges'
    named_styles: ListOfElement(NamedStyle) = 'namedStyles.styles'
    suggested_named_styles: str = 'suggestedNamedStylesChanges'
    lists: DictOfElement(List) = 'lists'
    named_ranges: DictOfElement(NamedRange) = 'namedRanges'
    revision: str = 'revisionId'
    suggestion_mode: str = 'suggestionsViewMode'
    inline_objects: DictOfElement(InlineOrPositionedObject) = 'inlineObjects'
    positioned_objects: DictOfElement(InlineOrPositionedObject) = 'positionedObjects'

    def as_html(self):
        return '\n'.join([q.as_html(self) for q in self.body])
