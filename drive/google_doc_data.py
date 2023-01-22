import json


# todo bring that out into a separate repo just for google doc parsing.


class Element:
    def __init__(self, element):
        self.element = element
        self._data = None
        if self.element is not None:
            self.process()

    def process(self):
        raise NotImplementedError()

    @property
    def data(self):
        return self._data


class TableOfContents(Element):
    suggested_insertions = None
    suggested_deletions = None

    def process(self):
        self.suggested_insertions = self.element.get('suggestedInsertionIds')
        self.suggested_deletions = self.element.get('suggestedDeletionIds')
        self._data = [StructuralElement(item) for item in self.element.get('content')]


class Dimension(Element):
    magnitude = None
    unit = None

    def process(self):
        self.magnitude = self.element.get('magnitude')
        self.unit = self.element.get('unit')
        self._data = f'{self.magnitude} {self.unit}'


class DimensionPack:
    def __init__(self, left=None, right=None, top=None, bottom=None):
        self.left = Dimension(left)
        self.right = Dimension(right)
        self.top = Dimension(top)
        self.bottom = Dimension(bottom)


class Size(Element):
    def process(self):
        self.height = self.element.get('height')
        self.width = self.element.get('width')


class ColumnProperties(Element):
    def process(self):
        """"widthType": enum (WidthType),  todo: create if necessary
                WIDTH_TYPE_UNSPECIFIED
                EVENLY_DISTRIBUTED
                FIXED_WIDTH
          "width": {
            object (Dimension)
          }
        """
        self._data = self.element
        self._data['width'] = Dimension(self._data['width'])


class TableStyle(Element):
    def process(self):
        self._data = [ColumnProperties(q) for q in self.element.get('tableColumnProperties')]


class TableRowStyle(Element):
    min_height: Dimension = None
    header: bool = None
    prevent_overflow: bool = None

    def process(self):
        self.min_height = Dimension(self.element.get('minRowHeight'))
        self.header = self.element.get('tableHeader')
        self.prevent_overflow = self.element.get('preventOverflow')


class Color(Element):
    def process(self):
        if 'rgbColor' in self.element:
            self._data = self.element.get('rgbColor')
        else:  # represents OptionalColor; currently considering all colors optional.
            self._data = self.element.get('color', {}).get('rgbColor')

    @property
    def hex(self):
        def to_hex(val: float):
            i_val = val * 256  # 256 to balance the curve of float values evenly
            if i_val == 256:
                i_val = 255
            return hex(int(i_val))[2:].zfill(2).upper()

        if self._data is None:
            return None

        return f'#{to_hex(self._data.get("red", 0))}' \
               f'{to_hex(self._data.get("green", 0))}' \
               f'{to_hex(self._data.get("blue", 0))}'


class Border(Element):  # represents Border and ParagraphBorder
    color: Color = None
    width: Dimension = None
    dash: str = None  # ENUM.
    padding: Dimension = None  # only for paragraphs
    prop_state: str = None  # enum for embedded

    def process(self):
        self.color = Color(self.element.get('color'))
        self.width = Dimension(self.element.get('width'))
        self.dash = self.element.get('dashStyle')
        self.padding = Dimension(self.element.get('padding'))
        self.prop_state = self.element.get('propertyState')


class TableCellStyle(Element):
    row_span: int = None
    col_span: int = None
    background: Color = None
    border_left: Border = None
    border_right: Border = None
    border_top: Border = None
    border_bottom: Border = None
    paddings: DimensionPack = None
    content_align: str = None  # ENUM

    def process(self):  # todo: may be this needs automation, too huge of a data structure.
        self.row_span = self.element.get("rowSpan")
        self.col_span = self.element.get("columnSpan")
        self.background = Color(self.element.get("backgroundColor"))
        self.border_left = Border(self.element.get("borderLeft"))
        self.border_right = Border(self.element.get("borderRight"))
        self.border_top = Border(self.element.get("borderTop"))
        self.border_bottom = Border(self.element.get("borderBottom"))
        self.paddings = DimensionPack(top=self.element.get('paddingTop'), bottom=self.element.get('paddingBottom'),
                                      left=self.element.get('paddingLeft'), right=self.element.get('paddingRight'))
        self.content_align = self.element.get('contentAlignment')


class TableCell(Element):
    start = None
    end = None
    suggested_insertions = None
    suggested_deletions = None
    style = None
    suggested_style = None

    def process(self):
        self.start = self.element.get('startIndex')
        self.end = self.element.get('endIndex')
        self.suggested_insertions = self.element.get("suggestedInsertionIds")
        self.suggested_deletions = self.element.get("suggestedDeletionIds")
        self.style = TableCellStyle(self.element.get('tableCellStyle'))
        self.suggested_style = self.element.get('suggestedTableCellStyleChanges')  # list of objects, not str
        self._data = [StructuralElement(q) for q in self.element.get('content')]


class TableRow(Element):
    start = None
    end = None
    suggested_insertions = None
    suggested_deletions = None
    style = None
    suggested_style = None

    def process(self):
        self.start = self.element.get('startIndex')
        self.end = self.element.get('endIndex')
        self.suggested_insertions = self.element.get("suggestedInsertionIds")
        self.suggested_deletions = self.element.get("suggestedDeletionIds")
        self.style = TableRowStyle(self.element.get('tableRowStyle'))
        self.suggested_style = self.element.get('suggestedTableRowStyleChanges')  # list of objects, not str
        self._data = [TableCell(q) for q in self.element.get('tableCells')]


class Table(Element):
    rows = 0
    columns = 0
    style = None
    suggested_insertions = None
    suggested_deletions = None

    def process(self):
        self.rows = self.element.get("rows")
        self.columns = self.element.get("columns")
        self.style = TableStyle(self.element.get("tableStyle"))
        self.suggested_insertions = self.element.get("suggestedInsertionIds")
        self.suggested_deletions = self.element.get("suggestedDeletionIds")
        self._data = [TableRow(q) for q in self.element.get("tableRows")]


class SectionStyle(Element):
    width: Dimension = None
    padding_end: Dimension = None
    separator: str = None  # Enum
    direction: str = None  # Enum
    margins: DimensionPack = None
    margin_header: Dimension = None
    margin_footer: Dimension = None
    section_type: str = None  # ENUM
    default_header_id: str = None
    default_footer_id: str = None
    first_page_header_id: str = None
    first_page_footer_id: str = None
    even_page_header_id: str = None
    even_page_footer_id: str = None
    use_first_page_header_footer: bool = None
    page_number_start: int = None

    def process(self):
        self.separator = self.element.get("columnSeparatorStyle")
        self.direction = self.element.get("contentDirection")
        self.margins = DimensionPack(top=self.element.get('marginTop'), bottom=self.element.get('marginBottom'),
                                     left=self.element.get('marginLeft'), right=self.element.get('marginRight'))
        self.margin_header = Dimension(self.element.get("marginHeader"))
        self.margin_footer = Dimension(self.element.get("marginFooter"))
        self.section_type = self.element.get("sectionType")
        self.default_header_id = self.element.get("defaultHeaderId")
        self.default_footer_id = self.element.get("defaultFooterId")
        self.first_page_header_id = self.element.get("firstPageHeaderId")
        self.first_page_footer_id = self.element.get("firstPageFooterId")
        self.even_page_header_id = self.element.get("evenPageHeaderId")
        self.even_page_footer_id = self.element.get("evenPageFooterId")
        self.use_first_page_header_footer = self.element.get("useFirstPageHeaderFooter")
        self.page_number_start = self.element.get("pageNumberStart")
        self.width = Dimension(self.element.get("columnProperties", {}).get('width'))
        self.padding_end = Dimension(self.element.get("columnProperties", {}).get('paddingEnd'))


class Link(Element):
    url: str = None
    bookmark_id: str = None
    heading_id: str = None

    def process(self):
        self.url = self.element.get('url')
        self.bookmark_id = self.element.get('bookmarkId')
        self.heading_id = self.element.get('headingId')


class Font(Element):
    font_family: str = None
    weight: int = None

    def process(self):
        self.font_family = self.element.get('fontFamily')
        self.weight = self.element.get('weight')


class BaseSuggested(Element):
    suggested_insertions = None
    suggested_deletions = None
    suggested_text_style: dict = None

    def __init__(self, element):
        super().__init__(element)
        if self.element is not None:
            self.suggested_insertions = self.element.get('suggestedInsertionIds')
            self.suggested_deletions = self.element.get('suggestedDeletionIds')
            self.suggested_text_style = self.element.get('suggestedTextStyleChanges')


class SectionBreak(BaseSuggested):
    def process(self):
        self._data = SectionStyle(self.element.get('sectionStyle'))


class Break(BaseSuggested):
    def process(self):
        self._data = TextStyle(self.element.get('textStyle'))


class TextStyle(Element):
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    small_caps: bool = False
    background: Color = None
    foreground: Color = None
    font_size: Dimension = None  # fixme default?
    weighted_font_family: Font = None
    baseline_offset: str = None  # ENUM
    link: Link = None

    def process(self):
        self.bold = self.element.get("bold")
        self.italic = self.element.get("italic")
        self.underline = self.element.get("underline")
        self.strikethrough = self.element.get("strikethrough")
        self.small_caps = self.element.get("smallCaps")
        self.background = Color(self.element.get("backgroundColor"))
        self.foreground = Color(self.element.get("foregroundColor"))
        self.font_size = Dimension(self.element.get("fontSize"))
        self.weighted_font_family = self.element.get("weightedFontFamily")
        self.baseline_offset = self.element.get("baselineOffset")
        self.link = Link(self.element.get("link"))

class CropProperties(Element):
    offset_left: int = None
    offset_right: int = None
    offset_top: int = None
    offset_bottom: int = None
    angle: int = None

    def process(self):
        self.offset_bottom = self.element.get('offsetBottom')
        self.offset_top = self.element.get('offsetTop')
        self.offset_right = self.element.get('offsetRight')
        self.offset_left = self.element.get('offsetLeft')
        self.angle = self.element.get('angle')

class ImageProperties(Element):
    source: str = None
    brightness: int = None
    contrast: int = None
    transparency: int = None
    crop: CropProperties = None
    angle: int = None
    def process(self):
        self._data = self.element.get('contentUri')
        self.source = self.element.get('soruceUri')
        self.brightness = self.element.get('brightness')
        self.contrast = self.element.get('contrast')
        self.transparency = self.element.get('transparency')
        self.crop = CropProperties(self.element.get('cropProperties'))
        self.angle = self.element.get('angle')


class EmbeddedObject(Element):
    title: str = None
    description: str = None
    border: Border = None
    size: Size = None
    margins: DimensionPack = None
    linked_content: dict = None  # spreadsheetId: str, chartId: int
    properties: ImageProperties = None  # embedded drawing ingested for completeness

    def process(self):
        self.title = self.element.get('title')
        self.description = self.element.get('description')
        self.border = Border(self.element.get('embeddedObjectBorder'))
        self.size = Size(self.element.get('size'))
        self.margins = DimensionPack(left=self.element.get('marginLeft'), right=self.element.get('marginRight'),
                                     top=self.element.get('marginTop'), bottom=self.element.get('marginBottom'))
        self.linked_content = self.element.get('linkedContentReference', {}).get('sheetsChartReference')
        self.properties = ImageProperties(self.element.get('embeddedDrawingProperties') or
                                          self.element.get('imageProperties'))


class ObjectProperties(Element):
    layout: str = None  # ENUM for Positioned
    offset: DimensionPack = None  # positioned, left top

    def process(self):
        self._data = EmbeddedObject(self.element.get('embeddedObject'))
        self.layout = self.element.get('positioning', {}).get('layout')
        self.offset = DimensionPack(left=self.element.get('positioning', {}).get('leftOffset'),
                                    top=self.element.get('positioning', {}).get('topOffset'))

class InlineOrPositionedObject(BaseSuggested):
    object_id: str = None
    suggested_properties: str = None
    def process(self):
        self.object_id = self.element.get('objectId')
        self._data = ObjectProperties(self.element.get('positionedObjectProperties') or
                                                  self.element.get('inlineObjectProperties'))
        self.suggested_properties = self.element.get('suggestedPositionedObjectPropertiesChanges') or \
                                    self.element.get('suggestedInlineObjectPropertiesChanges')



class TextRun(BaseSuggested):
    style: TextStyle = None

    def process(self):
        self._data = self.element.get('content')
        self.style = TextStyle(self.element.get('textStyle'))


class ParagraphElement(Element):
    start: int = 0
    end: int = None
    text_run: TextRun = None
    auto_text: dict = None  # todo parse those
    page_break: Break = None
    column_break: Break = None
    footnote_ref: dict = None
    horizontal_rule: Break = None
    equation: dict = None  # todo parse?
    inline_object_id: str = None
    person: dict = None  # todo parse?
    rich_link: dict = None  # google link, todo parse?

    def process(self):
        self.start = self.element.get('startIndex')
        self.end = self.element.get('endIndex')
        self.text_run = TextRun(self.element.get('textRun'))
        self.auto_text = self.element.get('autoText')
        self.page_break = Break(self.element.get('pageBreak'))
        self.column_break = Break(self.element.get('columnBreak'))
        self.footnote_ref = self.element.get('footnoteReference')
        self.horizontal_rule = Break(self.element.get('horizontalRule'))
        self.equation = self.element.get('equation')
        self.inline_object_id = self.element.get('inlineObjectElement', {}).get('inlineObjectId')
        self.person = self.element.get('person')
        self.rich_link = self.element.get('richLink')


class ParagraphStyle(Element):
    heading: str = None
    named_style: str = None
    alignment: str = None
    line_spacing: int = None
    direction: str = None
    spacing_mode: str = None
    space_above: Dimension = None
    space_below: Dimension = None
    border_between: Border = None
    border_top: Border = None
    border_bottom: Border = None
    border_left: Border = None
    border_right: Border = None
    first_line_indent: Dimension = None
    indent_start: Dimension = None
    tab_stops: list = None
    keep_lines_together: bool = None
    keep_with_next: bool = None
    avoid_widow_and_orphan: bool = None
    shading: Color = None
    page_break_before: bool = None
    """
        The ParagraphStyle on a Paragraph inherits from the paragraph's corresponding named style type.
        The ParagraphStyle on a named style inherits from the normal text named style.
        The ParagraphStyle of the normal text named style inherits from the default paragraph style in the Docs editor.
        The ParagraphStyle on a Paragraph element that's contained in a table may inherit its paragraph style from the table style.
    """

    def process(self):
        self.heading = self.element.get('headingId')
        self.named_style = self.element.get('namedStyleType')  # ENUM
        self.alignment = self.element.get('alignment')  # ENUM
        self.line_spacing = self.element.get('lineSpacing')  # int
        self.direction = self.element.get('direction')  # ENUM
        self.spacing_mode = self.element.get('spacingMode')  # ENUM
        self.space_above = Dimension(self.element.get('spaceAbove'))
        self.space_below = Dimension(self.element.get('spaceBelow'))
        self.border_between = Border(self.element.get('borderBetween'))
        self.border_top = Border(self.element.get('borderTop'))
        self.border_bottom = Border(self.element.get('borderBottom'))
        self.border_left = Border(self.element.get('borderLeft'))
        self.border_right = Border(self.element.get('borderRight'))
        self.first_line_indent = Dimension(self.element.get('indentFirstLine'))
        self.indent_start = Dimension(self.element.get('indentStart'))
        self.tab_stops = self.element.get('tabStops')
        self.keep_lines_together = self.element.get('keepLinesTogether')
        self.keep_with_next = self.element.get('keepWithNext')
        self.avoid_widow_and_orphan = self.element.get('avoidWidowAndOrphan')
        self.shading = Color(self.element.get('shading', {}).get('backgroundColor'))
        self.page_break_before = self.element.get('pageBreakBefore')


class Bullet(Element):
    list_id: str = None
    nesting_level: int = None
    text_style: TextStyle = None

    def process(self):
        self.list_id = self.element.get('listId')
        self.nesting_level = self.element.get('nestingLevel')
        self.text_style = TextStyle(self.element.get('textStyle'))


class Paragraph(Element):
    style: ParagraphStyle = None
    suggested_style: dict = None  # fixme: might be wrong datatype
    bullet: Bullet = None
    suggested_bullet: str = None
    positioned: list = None  # todo parse this
    suggested_positioned: dict = None
    """
    Newline terminated content (!)
    """

    def process(self):
        self._data = [ParagraphElement(item) for item in self.element.get('elements')]
        self.style = ParagraphStyle(self.element.get('paragraphStyle'))
        self.suggested_style = self.element.get('suggestedParagraphStyleChanges')
        self.bullet = self.element.get('bullet')  # present if paragraph is part of a list.
        self.suggested_bullet = self.element.get('suggestedBulletChanges')
        self.positioned = self.element.get('positionedObjectIds')
        self.suggested_positioned = self.element.get('suggestedPositionedObjectIds')


class StructuralElement(Element):
    start = None
    end = None

    def process(self):
        """
        self.element expected structure.
        Names of arguments need to follow Google Docs json format.
        :startIndex: Missing if 0.
        :endIndex: Mandatory.
        :paragraph: One possible value for the element type
        :sectionBreak: One possible value for the element type
        :table: One possible value for the element type
        :tableOfContents: One possible value for the element type
        """
        self.start = self.element.get('startIndex', 0)
        self.end = self.element.get('endIndex')
        if tuple(q for q in ('paragraph', 'sectionBreak', 'table', 'tableOfContents')
                 if self.element.get(q) is not None).__len__() > 1:
            raise AttributeError(f'Structural element got more than one type set:'
                                 f'paragraph: {self.element.get("paragraph")}, '
                                 f'sectionBreak: {self.element.get("sectionBreak")}, '
                                 f'table: {self.element.get("table")},'
                                 f'tableOfContents: {self.element.get("tableOfContents")}')
        if self.element.get("paragraph") is not None:
            self._data = Paragraph(self.element.get("paragraph"))
        elif self.element.get("sectionBreak") is not None:
            self._data = SectionBreak(self.element.get("sectionBreak"))
        elif self.element.get("table") is not None:
            self._data = Table(self.element.get("table"))
        elif self.element.get("tableOfContents") is not None:
            self._data = TableOfContents(self.element.get("tableOfContents"))
        else:
            raise AttributeError(f'No type of structural element found!')


class Heading(Element):
    heading_id: str = None

    def process(self):
        self.heading_id = self.element.get('headerId') or self.element.get('footerId') or self.element.get('footnoteId')
        self._data = self.element.get('content')


class DocumentStyle(Element):
    background: Color = None
    default_header_id: str = None
    default_footer_id: str = None
    even_page_header_id: str = None
    even_page_footer_id: str = None
    first_page_header_id: str = None
    first_page_footer_id: str = None
    use_first_page_header_footer: bool = False
    use_even_page_header_footer: bool = False
    page_number_start: int = None
    margins: DimensionPack = None
    size: Size = None
    margin_header: Dimension = None
    margin_footer: Dimension = None
    custom_margins_h_f: bool = None

    def process(self):
        self.background = Color(self.element.get('background'))
        self.default_header_id = self.element.get('defaultHeaderId')
        self.default_footer_id = self.element.get("defaultFooterId")
        self.even_page_header_id = self.element.get("evenPageHeaderId")
        self.even_page_footer_id = self.element.get("evenPageFooterId")
        self.first_page_header_id = self.element.get("firstPageHeaderId")
        self.first_page_footer_id = self.element.get("firstPageFooterId")
        self.use_first_page_header_footer = self.element.get("useFirstPageHeaderFooter")
        self.use_even_page_header_footer = self.element.get("useEvenPageHeaderFooter")
        self.page_number_start = self.element.get("pageNumberStart")
        self.margins = DimensionPack(top=self.element.get('marginTop'), bottom=self.element.get('marginBottom'),
                                     left=self.element.get('marginLeft'), right=self.element.get('marginRight'))
        self.size = Size(self.element.get('pageSize'))
        self.margin_header = self.element.get('marginHeader')
        self.margin_footer = self.element.get('marginFooter')
        self.custom_margins_h_f = self.element.get('useCustomHeaderFooterMargins')


class NamedStyle(Element):
    style_type: str = None
    text_style: TextStyle = None
    paragraph_style: ParagraphStyle = None

    def process(self):
        self.style_type = self.element.get('namedStyleType')
        self.text_style = self.element.get('textStyle')
        self.paragraph_style = self.element.get('paragraphStyle')


class NestingLevel(Element):
    bullet_alignment: str = None  # enum
    glyph_format: str = None
    indent_first_line: Dimension = None
    indent_start: Dimension = None
    text_style: TextStyle = None
    start_number: int = None
    glyph: str = None  # enum or the character itself (!)

    def process(self):
        self.bullet_alignment = self.element.get('bulletAlignment')
        self.glyph_format = self.element.get('glyphFormat')
        self.indent_first_line = Dimension(self.element.get('indentFirstLine'))
        self.indent_start = Dimension(self.element.get('indentStart'))
        self.text_style = TextStyle(self.element.get('textStyle'))
        self.start_number = self.element.get('startNumber')
        self.glyph = self.element.get('glyphType') or self.element.get('glyphSymbol')


class List(BaseSuggested):
    suggsted_properties: str = None

    def process(self):
        self.suggsted_properties = self.element.get('suggestedListPropertiesChanges')
        self._data = {}
        cnt = 0
        for list_prop in self.element.get('listProperties', {}).get('nestingLevels', []):
            self._data[cnt] = NestingLevel(list_prop)
            cnt += 1

class Range(Element):
    segment_id: str = None
    start_index: int = 0
    end_index: int = None

    def process(self):
        self._data = self.element.get('segmentId')
        self.start_index = self.element.get('startIndex', 0)
        self.end_index = self.element.get('endIndex')

class NamedRange(Element):
    name_range_id: str = None
    name: str = None

    def process(self):
        self.name_range_id = self.element.get('namedRangeId')
        self.name = self.element.get('name')
        self._data = [Range(q) for q in self.element.get('ranges')]


class GoogleDoc:
    def __init__(self, bytes_or_str=None, json_data=None):
        if json_data is None and bytes_or_str is None:
            raise ValueError(f'Provide either bytes_data or json_data for GoogleDocData')
        elif json_data is None:
            json_data = json.loads(bytes_or_str if isinstance(bytes_or_str, str) else bytes_or_str.decode())

        def gen_dict(json_elem, cls):
            return {k: cls(json_elem[k]) for k in json_elem}

        self.title = json_data.get('title')
        self.doc_id = json_data.get('document_id')
        self.body = [StructuralElement(q) for q in json_data.get('body', {}).get('content')]
        self.headers = gen_dict(json_data.get('headers', {}), Heading)
        self.footers = gen_dict(json_data.get('footers', {}), Heading)
        self.footnotes = gen_dict(json_data.get('footnotes', {}), Heading)
        self.style = DocumentStyle(json_data.get('documentStyle'))
        self.suggested_style = json_data.get('suggestedDocumentStyleChanges')
        self.named_styles = [NamedStyle(q) for q in json_data.get('namedStyles', {}).get('styles', [])]
        self.suggested_named_styles = json_data.get('suggestedNamedStylesChanges')
        self.lists = gen_dict(json_data.get('lists', {}), List)
        self.named_ranges = gen_dict(json_data.get('namedRanges', {}), NamedRange)
        self.revision = json_data.get('revisionId')
        self.suggestion_mode = json_data.get('suggestionsViewMode')
        self.inline_objects = gen_dict(json_data.get('inlineObjects', {}), InlineOrPositionedObject)
        self.positioned_objects = gen_dict(json_data.get('positionedObjects', {}), InlineOrPositionedObject)

    def serialize(self) -> dict:
        pass


if __name__ == '__main__':
    import pickle

    with open('test_gdoc.pcl', 'rb') as f:
        data = pickle.load(f)
    g = GoogleDoc(json_data=data)
    print(g)
