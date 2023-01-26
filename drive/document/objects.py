from .json_dataclass import Element, Field, PackField
from .style import Border, Size, DimensionPack
from .attr_mixins import Suggested


class CropProperties(Element):
    offset_left: int = 'offsetBottom'
    offset_right: int = 'offsetTop'
    offset_top: int = 'offsetRight'
    offset_bottom: int = 'offsetLeft'
    angle: int = 'angle'


class ImageProperties(Element):
    content: str = 'contentUri'
    source: str = 'soruceUri'
    brightness: int = 'brightness'
    contrast: int = 'contrast'
    transparency: int = 'transparency'
    crop: CropProperties = 'cropProperties'
    angle: int = 'angle'

    def as_html(self, root):
        return f'<img src="{self.source}" style="{self.as_css(root)}">'

    def as_css(self, root):
        return ""

class EmbeddedObject(Element):
    title: str = 'title'
    description: str = 'description'
    border: Border = 'embeddedObjectBorder'
    size: Size = 'size'
    margins: DimensionPack = PackField(('marginLeft', 'marginRight', 'marginTop', 'marginBottom'))
    linked_content: dict = 'linkedContentReference.sheetsChartReference'  # spreadsheetId: str, chartId: int
    properties: ImageProperties = 'embeddedDrawingProperties.imageProperties'  # embedded drawing ingested for completeness

    def as_html(self, root):
        if self.title == 'horizontal line':
            return f'<hr style="{self.as_css(root)}">'
        if self.properties is not None:
            return f'<div style={self.as_css(root)}>{self.properties.as_html(root)}</div>'
        return 'object'

    def as_css(self, root):
        brd = "" if self.border is None else f'border: {self.border.as_css(root)};'
        mrg = "" if self.margins is None else self.margins.as_css(root)
        return f"{brd}{mrg}"

class ObjectProperties(Element):
    content: EmbeddedObject = 'embeddedObject'
    layout: str = 'positioning.layout'  # ENUM for Positioned
    offset: DimensionPack = PackField(('positioning.leftOffset', 'positioning.topOffset'))  # positioned, left top

    def as_html(self, root):
        return f'<div style={self.offset.as_css(root)}>{self.content.as_html(root)}</div>'

class InlineOrPositionedObject(Element, Suggested):
    content: ObjectProperties = Field('positionedObjectProperties', alt_names=('inlineObjectProperties',))
    object_id: str = 'objectId'

    def as_html(self, root):
        return self.content.as_html(root)