from .json_dataclass import Element, ListOfElement, BackReference
from .attr_mixins import Suggested


class TableOfContents(Element, Suggested):
    content: ListOfElement(BackReference('StructuralElement')) = 'content'

    def as_html(self, root):
        return self.content.as_html(root)
