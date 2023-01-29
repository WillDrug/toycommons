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
from dataclasses import dataclass


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

    def as_html(self, root):  # deprecated
        return self.content.as_html(root)

    @property
    def content_class(self):
        return self.content.__class__


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


@dataclass
class CSSStructure:
    outer_div = 'container'
    table_of_contents = 'table_of_contents'
    table = "table"
    table_row = "table-row"
    table_header = "table-header"
    table_column = "table-column"
    section = "section"
    section_columned = "section-cols"
    structural_element = 'struct-element'
    paragraph = 'paragraph'
    mailto = 'mailto'
    url = 'url'
    list = 'list'
    image = 'img'
    span = 'span'
    named_style_tag = {
        'NAMED_STYLE_TYPE_UNSPECIFIED': 'p',
        'NORMAL_TEXT': 'p',
        'TITLE': 'p',
        'SUBTITLE': 'p',
        'HEADING_1': 'h1',
        'HEADING_2': 'h2',
        'HEADING_3': 'h3',
        'HEADING_4': 'h4',
        'HEADING_5': 'h5',
        'HEADING_6': 'h6'
    }
    named_style_tag_default = 'p'
    named_style_class = {
        'NAMED_STYLE_TYPE_UNSPECIFIED': '',
        'NORMAL_TEXT': '',
        'TITLE': 'title',
        'SUBTITLE': 'subtitle',
        'HEADING_1': 'heading',
        'HEADING_2': 'heading',
        'HEADING_3': 'heading',
        'HEADING_4': 'heading',
        'HEADING_5': 'heading',
        'HEADING_6': 'heading'
    }
    hr = 'hr_class'

class HTMLConverter:
    @staticmethod
    def style_dict_to_string(style_dict):
        return ';'.join([f'{k}: {style_dict[k]}' for k in style_dict])

    def process_object(self, obj):
        if obj is None:
            return ''
        obj = obj.content
        if obj.content.title == 'horizontal line':
            return f'<hr class="{self.css_classes.hr}">'
        e_style = ''
        if obj.positioning is not None:
            e_style = obj.positioning.as_css()
        return f'<img src="{obj.content.properties.source or obj.content.properties.content}" ' \
               f'class="{self.css_classes.image}" ' \
               f'style="{obj.content.margins.as_css()};' \
               f'{obj.content.size.as_css()};{e_style}" alt="{obj.content.title} : {obj.content.description}">'

    def __init__(self, google_doc: GoogleDoc, css_classes=None):
        if css_classes is None:
            css_classes = CSSStructure()
        self.css_classes = css_classes
        self.doc = google_doc
        self.title = self.doc.title

    def body_as_html(self):
        sections = {0: []}
        section_styles = {0: None}
        key = 0
        for struct in self.doc.body:
            if isinstance(struct.content, SectionBreak):
                key += 1
                sections[key] = []
                section_styles[key] = struct.content.content
            else:
                sections[key].append(struct)
        data = ''

        for section_num in range(max(sections.keys())+1):
            if sections[section_num].__len__() == 0:  # I don't trust google.
                continue
            style, cols = section_styles[section_num].as_css()
            classes = self.css_classes.section
            # turn cols into percetange max width
            cols_style = ''
            style_override = {}
            if cols.__len__() > 0:
                classes += " " + self.css_classes.section_columned
                style_override['max-width'] = f'{100/cols.__len__()-0.1}%'
                cols_style = f'column-count: {cols.__len__()};'

            data += f'<div class="{classes}" style="{cols_style}{style}">'
            for elem in sections[section_num]:
                data += f'<div class="{self.css_classes.structural_element}" ' \
                        f'style="{self.style_dict_to_string(style_override)}">' + \
                        self.process_structural_element(elem) + '</div>'
            data += '</div>'

        return f'<div class="{self.css_classes.outer_div}">{data}</div>'

    def process_structural_element(self, elem: StructuralElement):
        if elem.content_class is TableOfContents:
            data = '\n'.join([self.process_structural_element(q) for q in elem.content.content])
            return f'<div class="{self.css_classes.table_of_contents}">{data}</div>'
        elif elem.content_class is Table:
            return self.process_table(elem.content)
        elif elem.content_class is Paragraph:
            return self.process_paragraph(elem.content)
        else:
            raise ValueError(f'Malformed GoogleDoc. Expected one of type got {elem.content_class}')

    def process_table(self, elem):
        column_styles = elem.style  # list of ColumnProperties class
        rows = []
        for row in elem.content:
            tag = 'th' if row.style.header else 'tr'
            css_class = self.css_classes.table_header if row.style.header else self.css_classes.table_row
            columns_data = self.process_row(row.content, column_styles)
            row_data = f'<{tag} class="{css_class}" style="min-height: {row.style.min_height.as_css()};">' \
                       f'{columns_data}</{tag}>'
            rows.append(row_data)
        data = '\n'.join(rows)
        return f'<table class={self.css_classes.table}">{data}</table>'

    def process_row(self, columns, styles: list):
        """ Style has "width_type" containing:
            WIDTH_TYPE_UNSPECIFIED
            EVENLY_DISTRIBUTED
            FIXED_WIDTH
        """
        data = []
        for i, col in enumerate(columns):
            idata = [self.process_structural_element(q) for q in col.content]
            idata = '\n'.join(idata)
            istyle = styles[i].as_css_dict()
            istyle.update(col.style.as_css_dict())
            data.append(f'<td class="{self.css_classes.table_column}" '
                        f'style="{self.style_dict_to_string(istyle)}">{idata}</td>')
        return '\n'.join(data)

    def process_paragraph(self, elem):
        glyph_equivalence = {
            'GLYPH_TYPE_UNSPECIFIED': ('disc', 'ul'),
            'NONE': ('disc', 'ul'),
            'DECIMAL': ('decimal', 'ol'),
            'ZERO_DECIMAL': ('decimal-leading-zero', 'ol'),
            'UPPER_ALPHA': ('upper-alpha', 'ol'),
            'ALPHA': ('lower-alpha', 'ol'),
            'UPPER_ROMAN': ('upper-roman', 'ol'),
            'ROMAN': ('lower-roman', 'ol')
        }
        style = elem.style.as_css_dict()

        tag = self.css_classes.named_style_tag.get(elem.style.named_style, self.css_classes.named_style_tag_default)
        extra_cls = self.css_classes.named_style_class.get(elem.style.named_style, '')

        # object processing
        objs_data = ''
        if elem.positioned_object_ids is not None:
            objs = [self.doc.positioned_objects.get(q) for q in elem.positioned_object_ids]
            objs_data = '\n'.join([self.process_object(q) for q in objs])

        data = f'<{tag} class="{self.css_classes.paragraph} {extra_cls}" ' \
               f'style="{self.style_dict_to_string(style)}">' + objs_data + '{}' + f'</{tag}>'
        if elem.bullet is not None:
            current_list = self.doc.lists.get(elem.bullet.list_id)
            level = current_list.nesting_levels[elem.bullet.nesting_level]
            l_style = {}
            l_style['list-style-type'], lst_tag = glyph_equivalence.get(level.glyph, (level.glyph, 'ul'))
            data.format(f'<{lst_tag} class="{self.css_classes.list}" '
                        f'style="{self.style_dict_to_string(l_style)}">' + '{}' + f'</{lst_tag}>')

        content = '\n'.join([self.process_paragraph_element(q) for q in elem.content])

        return data.format(content)

    def process_paragraph_element(self, elem):
        # fixme change debug strings to something
        if elem.text_run is not None:
            return self.process_text_run(elem.text_run)
        if elem.auto_text is not None:  # no page numbers!
            return ''
        if elem.page_break is not None:  # no pages!
            return ''
        if elem.column_break is not None:
            return 'YOU NEED TO PARSE COLUMN BREAKS NOW BITCH'
        if elem.footnote_ref is not None:
            return ''  # NO FOOTNOTES
        if elem.horizontal_rule is not None:
            return f'<hr class="{self.css_classes.hr}">'
        if elem.equation is not None:
            return ''  # NO EQUATIONS LOL
        if elem.inline_object_id is not None:
            obj = self.doc.inline_objects.get(elem.inline_object_id)
            return self.process_object(obj)
        if elem.person is not None:  # todo: text style
            name = elem.person['personProperties'].get('name')
            mail = elem.person['personProperties'].get('email')
            return f'<a href="mailto:{mail}" class="{self.css_classes.mailto}">{name}</a>'
        if elem.rich_link is not None:  # todo: text style
            title = elem.rich_link.get('richLinkProperties', {}).get('title', '')
            uri = elem.rich_link.get('richLinkProperties', {}).get('uri', '')
            return f'<a href="{uri}" class="{self.css_classes.url}">{title}</a>'
        return 'NOTHING IS REAL'

    def process_text_run(self, elem):
        style_text = self.style_dict_to_string(elem.style.as_css_dict())
        return f'<span class="{self.css_classes.span}" style="{style_text}">{elem.content}</span>'

