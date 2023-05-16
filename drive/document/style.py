from .json_dataclass import Element, Field, PackField


class Dimension(Element):
    magnitude: int = 'magnitude'
    unit: str = 'unit'

    def as_css(self):
        if self.magnitude is None:
            return ''
        return f'{self.magnitude}{self.unit}'

    def __eq__(self, other):
        if other is None:
            return None
        return self.unit == other.unit and self.magnitude == other.magnitude


class DimensionPack(Element):
    top: Dimension = Field('marginTop', alt_names=('paddingTop', 'positioning.topOffset'))
    left: Dimension = Field('marginLeft', alt_names=('paddingLeft', 'positioning.leftOffset'))
    bottom: Dimension = Field('marginBottom', alt_names=('paddingBottom',))
    right: Dimension = Field('marginRight', alt_names=('paddingRight',))

    def as_css_dict(self, field="margin"):
        out = {}
        if self.top is not None and self.top.as_css() is not None:
            out[f'{field}-top'] = self.top.as_css()
        if self.bottom is not None and self.bottom.as_css() is not None:
            out[f'{field}-bottom'] = self.bottom.as_css()
        if self.right is not None and self.right.as_css() is not None:
            out[f'{field}-right'] = self.right.as_css()
        if self.left is not None and self.left.as_css() is not None:
            out[f'{field}-left'] = self.left.as_css()
        return out

    def as_css(self, field="margin"):
        def get_val(name, i_field):
            if i_field is None or i_field.as_css() is None or i_field.as_css() == '':
                return ''
            return f'{name}: {i_field.as_css()};'

        return f'{get_val(f"{field}-top", self.top)} {get_val(f"{field}-bottom", self.bottom)}' \
               f'{get_val(f"{field}-left", self.left)} {get_val(f"{field}-right", self.right)}'


class Size(Element):
    height: Dimension = 'height'
    width: Dimension = 'width'

    def as_css(self):
        h = '' if self.height is None or self.height.as_css() is None else f'height: {self.height.as_css()}'
        w = '' if self.width is None or self.width.as_css() is None else f'width: {self.width.as_css()}'
        return f'{h};{w}'


class Color(Element):
    color: dict = Field('rgbColor', alt_names=('color.rgbColor',))

    def as_css(self, ignore_ignoration=False):
        def to_hex(val: float):
            i_val = val * 256  # 256 to balance the curve of float values evenly
            if i_val == 256:
                i_val = 255
            return hex(int(i_val))[2:].zfill(2).upper()

        if self.color is None:
            return None

        return f'#{to_hex(self.color.get("red", 0))}' \
               f'{to_hex(self.color.get("green", 0))}' \
               f'{to_hex(self.color.get("blue", 0))}'

    def __eq__(self, other):
        if other is None:
            return False
        return self.color == other.color

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

    def get_dash(self):
        return {
            'DOT': 'dotted',
            'DASH': 'dashed',
        }.get(self.dash, 'solid')

    def as_css_dict(self, side=None):
        width = self.width
        if width is None or width.magnitude is None:
            return None
        pretag = 'border' if side is None else f'border-{side}'
        out = {
            f'{pretag}-width': width.as_css(),
            f'{pretag}-style': self.get_dash()
        }
        if self.color is not None and self.color.as_css() is not None:
            out[f'{pretag}-color'] = self.color.as_css()
        return out

    def as_css(self, side=None):
        width = self.width
        if width is None:
            return None
        if width.magnitude is None:
            return None
        dash = self.dash
        if dash == 'DOT':
            dash = 'dotted'
        elif dash == 'DASH':
            dash = 'dashed'
        else:  # dash == 'DASH_STYLE_UNSPECIFIED' or dash == 'SOLID':
            dash = 'solid'
        color = self.color.as_css()
        pretag = 'border' if side is None else f'border-{side}'

        output = f'{pretag}-style: {dash}; {pretag}-width: {width.as_css()}'
        if color is not None:
            output += f'; {pretag}-color: {color}'

        return output


class Font(Element):
    font_family: str = 'fontFamily'
    weight: int = 'weight'

    def as_css_dict(self):
        return {
            'font-family': self.font_family,
            'font-weight': self.weight
        }


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

    def as_css_dict(self, previous_border=False, next_border=False):
        output = {}
        if self.space_above is not None and self.space_above.magnitude is not None:
            output['margin-top'] = self.space_above.as_css()
        if self.space_below is not None and self.space_below.magnitude is not None:
            output['margin-bottom'] = self.space_below.as_css()

        if self.border_between is not None:
            if previous_border:
                output.update(self.border_between.as_css_dict('top') or {})
            if next_border:
                output.update(self.border_between.as_css_dict('bottom') or {})

        if self.border_bottom and not next_border:
            output.update(self.border_bottom.as_css_dict('bottom') or {})
        if self.border_top and not previous_border:
            output.update(self.border_top.as_css_dict('top') or {})

        if self.border_right:
            output.update(self.border_right.as_css_dict('right') or {})
        if self.border_left:
            output.update(self.border_left.as_css_dict('left') or {})
        if self.shading is not None and self.shading.as_css() is not None:
            output['background'] = self.shading.as_css()
        if self.line_spacing is not None:
            output['line-height'] = f'{self.line_spacing}%'
        alignment = {
            'START': 'left',
            'CENTER': 'center',
            'END': 'right',
            'JUSTIFIED': 'justified'
        }
        output['text-align'] = alignment.get(self.alignment, 'inherit')

        return output


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

    def __add__(self, other):
        out = {}
        for attr in self._attributes:
            if getattr(self, attr) == getattr(other, attr):
                data = getattr(self, attr)
                if data.__class__ in (Color, Dimension):
                    data = data._json_data

                key = getattr(self.__class__, attr)
                out[key] = data

        return TextStyle(out)

    def as_css_dict(self, ignore_ignoration=False):
        out = {}
        if self.background is not None and self.background.as_css() is not None:
            out['background'] = self.background.as_css()
        if self.foreground is not None and self.foreground.as_css() is not None:
            out['color'] = self.foreground.as_css(ignore_ignoration=False)
        if self.strikethrough or self.underline:
            out['text-decoration'] = ''
        if self.underline:
            out['text-decoration'] = 'underline'
        if self.strikethrough:
            out['text-decoration'] += ' line-through'
        if self.weighted_font_family is not None:
            out.update(self.weighted_font_family.as_css_dict())
        if self.bold:
            out['font-weight'] = 'bold'
        return out


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
