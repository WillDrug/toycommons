from .json_dataclass import ListOfElement, Element, PackField, Field, BackReference
from .attr_mixins import Suggested
from .style import Dimension, Color, Border, DimensionPack


class ColumnProperties(Element):
    width_type: str = 'widthType'  # ENUM
    width: Dimension = 'width'

    def as_css(self, root):
        return f"width: {self.width.as_css(root)}"

    def as_css_dict(self):
        return {'width': self.width.as_css()}


class TableRowStyle(Element):
    min_height: Dimension = 'minRowHeight'
    header: bool = 'tableHeader'
    prevent_overflow: bool = 'preventOverflow'

    def as_css_dict(self):
        return {'min-height': self.min_height.as_css()}



class TableCellStyle(Element):
    row_span: int = 'rowSpan'
    col_span: int = 'columnSpan'
    background: Color = 'backgroundColor'
    border_left: Border = 'borderLeft'
    border_right: Border = 'borderRight'
    border_top: Border = 'borderTop'
    border_bottom: Border = 'borderBottom'
    paddings: DimensionPack = PackField(('paddingTop', 'paddingBottom', 'paddingLeft', 'paddingRight'))
    content_align: str = 'contentAlignment'  # ENUM

    def as_css_dict(self):
        out = {}
        if self.border_left is not None:
            out.update(self.border_left.as_css_dict('left') or {})
        if self.border_top is not None:
            out.update(self.border_left.as_css_dict('top') or {})
        if self.border_right is not None:
            out.update(self.border_left.as_css_dict('right') or {})
        if self.border_bottom is not None:
            out.update(self.border_left.as_css_dict('bottom') or {})
        if self.paddings is not None:
            out.update(self.paddings.as_css_dict('padding') or {})
        if self.content_align in ['TOP', 'MIDDLE', 'BOTTOM']:
            out['vertical-align'] = {'TOP': 'top', 'MIDDLE': 'middle', 'BOTTOM': 'bottom'}.get(self.content_align)
        return out

    def as_css(self):
        def add_field(field, value):
            if value is None:
                return ''
            else:
                return f'{field}: {value};'

        return f'{add_field("background", self.background.as_css())}' \
               f'{add_field("border-left", self.border_left.as_css(side="left"))}' \
               f'{add_field("border-right", self.border_right.as_css(side="right"))}' \
               f'{add_field("border-top", self.border_top.as_css(side="top"))}' \
               f'{add_field("border-bottom", self.border_bottom.as_css(side="bottom"))}' \
               f'{add_field("padding", self.paddings.as_css())}'


class TableCell(Element, Suggested):
    start: int = Field('startIndex', default=0)
    end: int = 'endIndex'
    style: TableCellStyle = 'tableCellStyle'
    content: ListOfElement(BackReference('StructuralElement')) = 'content'


class TableRow(Element, Suggested):
    start: int = Field('startIndex', default=0)
    end: int = 'endIndex'
    style: TableRowStyle = 'tableRowStyle'
    content: ListOfElement(TableCell) = 'tableCells'


class Table(Element, Suggested):
    rows: int = 'rows'
    columns: int = 'columns'
    style: ListOfElement(ColumnProperties) = 'tableStyle.tableColumnProperties'
    content: ListOfElement(TableRow) = 'tableRows'
