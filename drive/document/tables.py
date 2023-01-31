from .json_dataclass import ListOfElement, Element, PackField, Field, BackReference
from .attr_mixins import Suggested
from .style import Dimension, Color, Border, DimensionPack
from math import floor


class ColumnProperties(Element):
    width_type: str = 'widthType'  # ENUM
    width: Dimension = 'width'

    def as_css_dict(self, col_num=None):
        if self.width_type == 'EVENLY_DISTRIBUTED' and col_num is not None:
            return {'width': f'{floor(100/col_num)}%'}
        if self.width is None or self.width.as_css() is None:
            return {}
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
        out = {}  # fixme: table alignment-spanning

        def update_border(field, side):
            nonlocal out
            if field is None:  # default border
                out.update(Border({'width': {'magnitude': 1, 'unit': 'PT'}}).as_css_dict(side))
            else:
                out.update(field.as_css_dict(side) or {})

        update_border(self.border_right, 'right')
        update_border(self.border_left, 'left')
        update_border(self.border_top, 'top')
        update_border(self.border_bottom, 'bottom')

        if self.paddings is not None:
            out.update(self.paddings.as_css_dict('padding') or {})
        if self.content_align in ['TOP', 'MIDDLE', 'BOTTOM']:
            out['vertical-align'] = {'TOP': 'top', 'MIDDLE': 'middle', 'BOTTOM': 'bottom'}.get(self.content_align)
        if self.background is not None:
            out['background'] = self.background.as_css()
        return out


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
