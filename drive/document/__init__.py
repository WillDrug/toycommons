import html
from typing import Union
from .json_dataclass.element import Element, DictOfElement, ListOfElement, Field
from .tables import Table
from .style import DocumentStyle, NamedStyle, Color, TextStyle
from .ranges import NamedRange
from .objects import InlineOrPositionedObject
from .lists import List
from .paragraph import Paragraph, Heading
from .table_of_contents import TableOfContents
from .layout import SectionBreak
from dataclasses import dataclass, field


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

    def get_image_objects(self):
        image_props = []
        if self.inline_objects is not None:
            image_props.extend([q for q in self.inline_objects.values()])
        if self.positioned_objects is not None:
            image_props.extend([q for q in self.positioned_objects.values()])
        return image_props


class ListWrapper:
    glyph_equivalence = {
        'GLYPH_TYPE_UNSPECIFIED': ('disc', 'ul'),
        'NONE': ('disc', 'ul'),
        'DECIMAL': ('decimal', 'ol'),
        'ZERO_DECIMAL': ('decimal-leading-zero', 'ol'),
        'UPPER_ALPHA': ('upper-alpha', 'ol'),
        'ALPHA': ('lower-alpha', 'ol'),
        'UPPER_ROMAN': ('upper-roman', 'ol'),
        'ROMAN': ('lower-roman', 'ol'),
        '●': ('disc', 'ul')
    }

    def __init__(self, lists: dict, bullet: "Bullet"):
        self.list_id = bullet.list_id
        self.level = bullet.nesting_level or 0
        self.local_style = bullet.text_style
        list_ref = lists.get(self.list_id).nesting_levels[self.level]
        style_type, self.lst_tag = self.glyph_equivalence.get(list_ref.glyph, ('disc', 'ul'))
        self.style_type = f'list-style-type: {style_type}'
        self.processing = False

    def tag(self):
        return self.glyph_equivalence.get(self.list_ref.glyph, (None, 'ul'))[1]

    def opening_tag(self, css_class):
        self.processing = True
        return f'<{self.lst_tag} class="{css_class}" style="{self.style_type}">'

    def closing_tag(self):
        return f'</{self.lst_tag}>'

    def __eq__(self, other):
        return self.list_id == other.list_id and self.level == other.level


@dataclass
class CSSStructure:
    outer_div: str = 'container'
    table_of_contents: str = 'table_of_contents'
    table: str = "table"
    table_row: str = "table-row"
    table_header: str = "table-header"
    table_column: str = "table-column"
    section: str = "section"
    section_columned: str = "section-cols"
    structural_element: str = 'struct-element'
    paragraph: str = 'paragraph'
    mailto: str = 'mailto'
    url: str = 'url'
    list: str = 'list'
    image: str = 'img'
    span: str = 'span'
    named_style_tag: dict = field(default_factory=lambda: {
        'NAMED_STYLE_TYPE_UNSPECIFIED': 'div',
        'NORMAL_TEXT': 'div',
        'TITLE': 'p',
        'SUBTITLE': 'p',
        'HEADING_1': 'h1',
        'HEADING_2': 'h2',
        'HEADING_3': 'h3',
        'HEADING_4': 'h4',
        'HEADING_5': 'h5',
        'HEADING_6': 'h6'
    })
    named_style_tag_default: str = 'p'
    named_style_class: dict = field(default_factory=lambda: {
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
    })
    hr: str = 'hr_class'


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
        # layout process!!
        if obj.positioning is not None:
            e_style = obj.positioning.as_css()
        if hasattr(obj.content.properties, 'local') and obj.content.properties.local is not None:
            img_src = obj.content.properties.local
        else:
            img_src = obj.content.properties.source or obj.content.properties.content

        return f'<img src="{img_src}" ' \
               f'class="{self.css_classes.image}" ' \
               f'style="{obj.content.margins.as_css()};' \
               f'{obj.content.size.as_css()};{e_style}" alt="{obj.content.title} : {obj.content.description}">'

    def __init__(self, google_doc: GoogleDoc, css_classes=None, ignore_black_white=False):
        self.ignore_black_white = ignore_black_white
        if css_classes is None:
            css_classes = CSSStructure()
        self.css_classes = css_classes
        self.doc = google_doc
        self.title = self.doc.title
        self.html_separator = ''
        self.__adjacent_paragraphs = {
            'prev': None,
            'next': None
        }

    def override_black_white(self):
        def wrapper(func):
            def inner(*args, **kwargs):
                chk = kwargs.pop('ignore_ignoration', False)
                res = func(*args, **kwargs)
                if chk:
                    return res
                if res is None:
                    return None
                if res.lower() == '#000000' or res.lower() == '#ffffff':
                    return None
                return res

            return inner

        backup = Color.as_css
        Color.as_css = wrapper(Color.as_css)
        return backup

    def get_adjacent(self, section_content, idx):
        try:
            elem = section_content[idx]
            if elem.content_class is Paragraph:
                return elem.content
        except IndexError:
            return None

    def body_as_html(self):
        if self.ignore_black_white:
            backup = self.override_black_white()
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

        for section_num in range(max(sections.keys()) + 1):
            if sections[section_num].__len__() == 0:  # I don't trust google.
                continue

            # here I tried to envelop paragraphs with common shading into another div
            # that doesn't help: borders will be split
            # if you preserve borders, you might end-up with non-balanced divs :(
            style, cols = section_styles[section_num].as_css()
            classes = self.css_classes.section
            # turn cols into percetange max width
            cols_style = ''
            style_override = {}
            if cols.__len__() > 0:
                classes += " " + self.css_classes.section_columned
                style_override['max-width'] = f'{100 / cols.__len__() - 0.1}%'
                cols_style = f'column-count: {cols.__len__()};'

            data += f'<div class="{classes}" style="{cols_style}{style}">'
            list_stack = []

            for i, elem in enumerate(sections[section_num]):
                self.__adjacent_paragraphs = {'next': self.get_adjacent(sections[section_num], i + 1),
                                              'prev': self.get_adjacent(sections[section_num], i - 1)}
                if elem.content_class is Paragraph:
                    if elem.content.bullet is not None:  # fixme this is horrifying D:
                        if list_stack.__len__() == 0:  # first list in a bunch, enclose in div
                            data += f'<div class="{self.css_classes.structural_element}" ' \
                                    f'style="{self.style_dict_to_string(style_override)}">'
                        wrapper = ListWrapper(self.doc.lists, elem.content.bullet)
                        if wrapper in list_stack:  # we know this list + level
                            while list_stack.__len__() > 0 and \
                                    list_stack[-1] != wrapper:
                                # close previous lists up to running one
                                curlist = list_stack.pop()
                                data += curlist.closing_tag()
                        elif list_stack.__len__() > 0:  #
                            while list_stack.__len__() > 0 and list_stack[-1].list_id != wrapper.list_id:
                                # there are other lists, we're closing them up to current list id
                                curlist = list_stack.pop()
                                data += curlist.closing_tag()
                        if list_stack.__len__() == 0 or list_stack[-1] != wrapper:
                            list_stack.append(wrapper)

                    if list_stack.__len__() > 0 and elem.content.bullet is None:
                        while list_stack.__len__() > 0:
                            curlist = list_stack.pop()
                            data += curlist.closing_tag()
                        data += '</div>'

                    if list_stack.__len__() == 0:
                        data += f'<div class="{self.css_classes.structural_element}" ' \
                                f'style="{self.style_dict_to_string(style_override)}">' + \
                                self.process_structural_element(elem) + '</div>'
                    else:
                        if list_stack.__len__() == 0:
                            raise ValueError(f'You screwed lists up!')
                        if not list_stack[-1].processing:
                            data += list_stack[-1].opening_tag(self.css_classes.list)
                        data += '<li>' + self.process_structural_element(elem) + '</li>'
                else:
                    if list_stack.__len__() > 0 and elem.content.bullet is None:
                        while list_stack.__len__() > 0:
                            curlist = list_stack.pop()
                            data += curlist.closing_tag()
                        data += '</div>'
                    data += f'<div class="{self.css_classes.structural_element}" ' \
                            f'style="{self.style_dict_to_string(style_override)}">' + \
                            self.process_structural_element(elem) + '</div>'

            if list_stack.__len__() > 0:
                while list_stack.__len__() > 0:
                    curlist = list_stack.pop()
                    data += curlist.closing_tag()
                data += '</div>'
            data += '</div>'
        if self.ignore_black_white:
            Color.as_css = backup
        return f'<div class="{self.css_classes.outer_div}">{data}</div>'

    def process_structural_element(self, elem: StructuralElement):
        if elem.content_class is TableOfContents:
            data = self.html_separator.join([self.process_structural_element(q) for q in elem.content.content])
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
        data = self.html_separator.join(rows)

        width = 'width: 100%;' if any([q.width_type == 'EVENLY_DISTRIBUTED' for q in column_styles]) else ''
        return f'<table style="border-collapse: collapse; max-width: 100%; {width}" ' \
               f'class={self.css_classes.table}">{data}</table>'

    def process_row(self, columns, styles: list):
        """ Style has "width_type" containing:
            WIDTH_TYPE_UNSPECIFIED
            EVENLY_DISTRIBUTED
            FIXED_WIDTH
        """
        data = []
        for i, col in enumerate(columns):
            idata = [self.process_structural_element(q) for q in col.content]
            idata = self.html_separator.join(idata)
            istyle = styles[i].as_css_dict(col_num=columns.__len__())
            istyle.update(col.style.as_css_dict())
            data.append(f'<td class="{self.css_classes.table_column}" '
                        f'style="{self.style_dict_to_string(istyle)}">{idata}</td>')
        return self.html_separator.join(data)

    def get_paragarph_style(self, elem: Paragraph):


        return style, remove

    def process_paragraph(self, elem: Paragraph):
        previous_border = None
        next_border = None
        if self.__adjacent_paragraphs['prev'] is not None:
            previous_border = self.__adjacent_paragraphs['prev'].style.border_bottom is not None and \
                              self.__adjacent_paragraphs['prev'].style.border_bottom.as_css() is not None

        if self.__adjacent_paragraphs['next'] is not None:
            next_border = self.__adjacent_paragraphs['next'].style.border_top is not None and \
                          self.__adjacent_paragraphs['next'].style.border_top.as_css() is not None


        elem_style = elem.style.as_css_dict(previous_border=previous_border, next_border=next_border)

        tag = self.css_classes.named_style_tag.get(elem.style.named_style, self.css_classes.named_style_tag_default)
        css_cls = self.css_classes.named_style_class.get(elem.style.named_style, '')
        css_cls += f' {self.css_classes.paragraph}'
        named_style = next((q for q in self.doc.named_styles if q.style_type == elem.style.named_style), None)
        if named_style is not None:
            style = named_style.paragraph_style.as_css_dict()
            style.update(elem_style)
        else:
            style = elem_style

        # upstreaming styles from inner elements to the paragraph;
        # THIS IS A HACK. Might cause troubles, but when I paint the full paragraph Google returns
        # me background for each text element separately for some reason.
        remove = ()
        if elem.content.__len__() > 1:
            common_style = None
            for s in elem.content:
                if s.text_run is not None:
                    if common_style is None:
                        common_style = s.text_run.style  # adding styles keeps only same elements.
                    else:
                        common_style = common_style + s.text_run.style
            common_style = common_style.as_css_dict(ignore_ignoration='background' in style)
            style.update(common_style)
            remove = tuple(common_style.keys())

        # object processing
        objs_data = ''
        if elem.positioned_object_ids is not None:
            objs = [self.doc.positioned_objects.get(q) for q in elem.positioned_object_ids]
            objs_data = self.html_separator.join([self.process_object(q) for q in objs])
        extra = ''
        if elem.style.heading is not None:
            extra += f'id="{elem.style.heading}"'
        data = f'<{tag} class="{css_cls}" {extra}' \
               f'style="{self.style_dict_to_string(style)}">' + objs_data + '{}' + f'</{tag}>'

        content = self.html_separator.join([
            self.process_paragraph_element(
                q,
                extra_style=None if named_style is None else named_style.text_style.as_css_dict(),
                backgrounded='background' in style,
                remove=remove
            )
            for q in elem.content])

        return data.format(content)

    def process_paragraph_element(self, elem, extra_style=None, backgrounded=False, remove=()):
        # fixme change debug strings to something
        if elem.text_run is not None:
            return self.process_text_run(elem.text_run, extra_style=extra_style,
                                         backgrounded=backgrounded, remove=remove)
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

    def process_text_run(self, elem, extra_style=None, backgrounded=False, remove=()):
        if elem.style.link is not None:
            tag = 'a'
            link = elem.style.link.url or f'#{elem.style.link.heading_id}'
            extra = f' href="{link}"'
        else:
            tag = 'span'
            extra = ''
        style = {}
        if extra_style is not None:
            style = extra_style
        style.update(elem.style.as_css_dict(ignore_ignoration=True))
        if not backgrounded and self.ignore_black_white and 'background' not in style:
            if 'color' in style:
                if style['color'].lower() in ['#000000', '#ffffff']:
                    del style['color']
        if ('background' in style or backgrounded) and 'color' not in style:
            style['color'] = '#000000'
        for r in remove:
            if r in style:
                del style[r]
        style_text = self.style_dict_to_string(style)
        text = html.escape(elem.content)  # .replace('\n', '')
        return f'<{tag} {extra} class="{self.css_classes.span}" style="{style_text}">' \
               f'{text}</{tag}>'
