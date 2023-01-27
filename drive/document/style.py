from .json_dataclass import Element, Field, PackField


class Dimension(Element):
    magnitude: int = 'magnitude'
    unit: str = 'unit'

    def as_css(self, root):
        if self.magnitude is None:
            return ''
        return f'{self.magnitude}{self.unit}'


class DimensionPack(Element):
    top: Dimension = Field('marginTop', alt_names=('paddingTop', 'topOffset'))
    left: Dimension = Field('marginLeft', alt_names=('paddingLeft', 'leftOffset'))
    bottom: Dimension = Field('marginBottom', alt_names=('paddingBottom',))
    right: Dimension = Field('marginRight', alt_names=('paddingRight',))

    def as_css(self, root, field="margin"):
        def get_val(name, field):
            if field is None or field.as_css(root) == '':
                return ''
            return f'{name}: {field.as_css(root)}'

        return f'{get_val(f"{field}-top", self.top)}; {get_val(f"{field}-bottom", self.bottom)};' \
               f'{get_val(f"{field}-left", self.left)}; {get_val(f"{field}-right", self.right)};'


class Size(Element):
    height: Dimension = 'height'
    width: Dimension = 'width'


class Color(Element):
    color: dict = Field('rgbColor', alt_names=('color.rgbColor',))

    def as_css(self, root):
        def to_hex(val: float):
            i_val = val * 256  # 256 to balance the curve of float values evenly
            if i_val == 256:
                i_val = 255
            return hex(int(i_val))[2:].zfill(2).upper()

        if self.color is None:
            return 'inherit'

        return f'#{to_hex(self.color.get("red", 0))}' \
               f'{to_hex(self.color.get("green", 0))}' \
               f'{to_hex(self.color.get("blue", 0))}'


class SpaceStyle:
    default_header_id: str = 'defaultHeaderId'
    default_footer_id: str = 'defaultFooterId'
    even_page_header_id: str = 'evenPageHeaderId'
    even_page_footer_id: str = 'evenPageFooterId'
    first_page_header_id: str = 'firstPageHeaderId'
    first_page_footer_id: str = 'firstPageFooterId'
    use_first_page_header_footer: bool = 'useFirstPageHeaderFooter'
    page_number_start: int = 'pageNumberStart'
    margins: DimensionPack = PackField(('marginTop', 'marginBottom', 'marginLeft', 'marginRight'))
    margin_header: Dimension = 'marginHeader'
    margin_footer: Dimension = 'marginFooter'


class Border(Element):  # represents Border and ParagraphBorder
    color: Color = 'color'
    width: Dimension = 'width'
    dash: str = 'dashStyle'  # ENUM.
    padding: Dimension = 'padding'  # only for paragraphs
    prop_state: str = 'propertyState'  # enum for embedded

    def as_css(self, root):
        return f'{self.dash.lower()} {self.width.as_css(root)} {self.color.as_css(root)}'


class Font(Element):
    font_family: str = 'fontFamily'
    weight: int = 'weight'

    def as_css(self, root):
        return f'font-family: {self.font_family}; font-weight: {self.weight};'


class ParagraphStyle(Element):
    heading: str = 'headingId'
    named_style: str = 'namedStyleType'
    alignment: str = 'alignment'
    line_spacing: int = 'lineSpacing'
    direction: str = 'direction'
    spacing_mode: str = 'spacingMode'
    space_above: Dimension = 'spaceAbove'
    space_below: Dimension = 'spaceBelow'
    border_between: Border = 'borderBetween'
    border_top: Border = 'borderTop'
    border_bottom: Border = 'borderBottom'
    border_left: Border = 'borderLeft'
    border_right: Border = 'borderRight'
    first_line_indent: Dimension = 'indentFirstLine'
    indent_start: Dimension = 'indentStart'
    tab_stops: list = 'tabStops'
    keep_lines_together: bool = 'keepLinesTogether'
    keep_with_next: bool = 'keepWithNext'
    avoid_widow_and_orphan: bool = 'avoidWidowAndOrphan'
    shading: Color = 'shading.backgroundColor'
    page_break_before: bool = 'pageBreakBefore'
    """
        The ParagraphStyle on a Paragraph inherits from the paragraph's corresponding named style type.
        The ParagraphStyle on a named style inherits from the normal text named style.
        The ParagraphStyle of the normal text named style inherits from the default paragraph style in the Docs editor.
        The ParagraphStyle on a Paragraph element that's contained in a table may inherit its paragraph style from the table style.
    """

    def as_css(self, root):
        base_style = ''

        def get_value(name, field):
            if field is None:
                return ""
            else:
                return f"{name}: {field.as_css(root)};"
        local_style = f"{get_value('margin-top', self.space_above)}{get_value('margin-bottom', self.space_below)}" \
                      f"{get_value('border-top', self.border_top)}{get_value('border-bottom', self.border_bottom)}" \
                      f"{get_value('border-left', self.border_left)}{get_value('border-right', self.border_right)}"
        return base_style + local_style


class Link(Element):
    url: str = 'url'
    bookmark_id: str = 'bookmarkId'
    heading_id: str = 'headingId'


class TextStyle(Element):
    bold: bool = 'bold'
    italic: bool = 'italic'
    underline: bool = 'underline'
    strikethrough: bool = 'strikethrough'
    small_caps: bool = 'smallCaps'
    background: Color = 'backgroundColor'
    foreground: Color = 'foregroundColor'
    font_size: Dimension = 'fontSize'  # fixme default?
    weighted_font_family: Font = 'weightedFontFamily'
    baseline_offset: str = 'baselineOffset'  # ENUM
    link: Link = 'link'

    def as_css(self, root):
        background = ""
        if self.background is not None:
            background = f'background: {self.background.as_css(root)};'
        foreground = ""
        if self.foreground is not None:
            foreground = f'color: {self.foreground.as_css(root)};'
        td = f'text-decoration: {"underline" if self.underline else ""} {"line-through" if self.strikethrough else ""};'
        return f'{"font-style: italic;" if self.italic else ""}' \
               f'{td if self.underline or self.strikethrough else ""}' \
               f'{background}' \
               f'{foreground}' \
               f'{"" if self.weighted_font_family is None else self.weighted_font_family.as_css(root)}' \
               f'{"font-weight: bold;" if self.bold else ""}'


class NamedStyle(Element):
    style_type: str = 'namedStyleType'
    text_style: TextStyle = 'textStyle'
    paragraph_style: ParagraphStyle = 'paragraphStyle'

    def paragraph_as_css(self, root):
        return self.text_style.as_css(root)

    def text_as_css(self, root):
        return self.text_style.as_css(root)


class DocumentStyle(Element, SpaceStyle):
    background: Color = 'background'
    use_even_page_header_footer: bool = 'useEvenPageHeaderFooter'
    size: Size = 'pageSize'
    custom_margins_h_f: bool = 'useCustomHeaderFooterMargins'
