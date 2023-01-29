from .json_dataclass import Element, Field, PackField
from .style import Border, Size, DimensionPack, Dimension
from .attr_mixins import Suggested


class CropProperties(Element):
    offset_left: int = 'offsetBottom'
    offset_right: int = 'offsetTop'
    offset_top: int = 'offsetRight'
    offset_bottom: int = 'offsetLeft'
    angle: int = 'angle'


class ImageProperties(Element):
    content: str = 'contentUri'
    source: str = 'sourceUri'
    brightness: int = 'brightness'
    contrast: int = 'contrast'
    transparency: int = 'transparency'
    crop: CropProperties = 'cropProperties'
    angle: int = 'angle'


class EmbeddedObject(Element):
    title: str = 'title'
    description: str = 'description'
    border: Border = 'embeddedObjectBorder'
    size: Size = 'size'
    margins: DimensionPack = PackField(('marginLeft', 'marginRight', 'marginTop', 'marginBottom'))
    linked_content: dict = 'linkedContentReference.sheetsChartReference'  # spreadsheetId: str, chartId: int
    properties: ImageProperties = Field('embeddedDrawingProperties.imageProperties', alt_names=('imageProperties',))

class Positioning(Element):
    left: Dimension = 'leftOffset'
    top: Dimension = 'topOffset'
    layout: str = 'layout'

    def as_css(self):
        layout = {
            'WRAP_TEXT': 'float: left;',
            'BREAK_LEFT': 'float: left; clear: left;',
            'BREAK_RIGHT': 'float: right; clear: right;',
            'IN_FRONT_OF_TEXT': 'position: absolute;',
            'BEHIND_TEXT': 'position: absolute;'
        }
        css = layout.get(self.layout, '')
        if 'position' not in css:
            css += 'position: relative;'
        return css+f'top: {self.top.as_css() or "0px"}; left: {self.left.as_css() or "0px"}'

class ObjectProperties(Element):
    content: EmbeddedObject = 'embeddedObject'
    layout: str = 'positioning.layout'  # ENUM for Positioned
    positioning: Positioning = 'positioning'  # positioned, left top


class InlineOrPositionedObject(Element, Suggested):
    content: ObjectProperties = Field('positionedObjectProperties', alt_names=('inlineObjectProperties',))
    object_id: str = 'objectId'
