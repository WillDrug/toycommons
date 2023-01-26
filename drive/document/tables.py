from .json_dataclass import ListOfElement, Element, PackField, Field, BackReference
from .attr_mixins import Suggested
from .style import Dimension, Color, Border, DimensionPack


class ColumnProperties(Element):
    width_type: str = 'widthType'  # ENUM
    width: Dimension = 'width'

    def as_css(self, root):
        return f"width: {self.width.as_css(root)}"

class TableRowStyle(Element):
    min_height: Dimension = 'minRowHeight'
    header: bool = 'tableHeader'
    prevent_overflow: bool = 'preventOverflow'

    def as_css(self, root):
        return f"min-height: {self.min_height.as_css(root)}"


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

    def as_css(self, root):
        return f'background: {self.background.as_css(root)}; border-left: {self.border_left.as_css(root)};' \
               f'border-right: {self.border_right.as_css(root)}; border-top: {self.border_top.as_css(root)};' \
               f'border-bottom: {self.border_bottom.as_css(root)}; ' \
               f'padding: {self.paddings.as_css(root, field="padding")};' \
               f'content-align: {self.content_align}'


class TableCell(Element, Suggested):
    start: int = Field('startIndex', default=0)
    end: int = 'endIndex'
    style: TableCellStyle = 'tableCellStyle'
    content: ListOfElement(BackReference('StructuralElement')) = 'content'

    def as_html(self, root, style: ColumnProperties):
        data = "\n".join([q.as_html(root) for q in self.content])
        return f'<td style="{style.as_css(root)}"><div style="{self.style.as_css(root)}">{data}</div></td>'


class TableRow(Element, Suggested):
    start: int = Field('startIndex', default=0)
    end: int = 'endIndex'
    style: TableRowStyle = 'tableRowStyle'
    content: ListOfElement(TableCell) = 'tableCells'

    def as_html(self, root, col_styles: list[ColumnProperties]):
        data = "\n".join([q.as_html(root, col_styles[i]) for i, q in enumerate(self.content)])
        return f'<{"th" if self.style.header else "tr"} style="{self.style.as_css(root)}">' \
               f'{data}</{"th" if self.style.header else "tr"}>'


class Table(Element, Suggested):
    rows: int = 'rows'
    columns: int = 'columns'
    style: ListOfElement(ColumnProperties) = 'tableStyle.tableColumnProperties'
    content: ListOfElement(TableRow) = 'tableRows'

    def as_html(self, root):
        data = "\n".join([q.as_html(root, self.style) for q in self.content])
        return f'<table>{data}</table>'
