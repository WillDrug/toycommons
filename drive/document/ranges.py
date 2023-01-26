from .json_dataclass import Element, ListOfElement, Field

class Range(Element):
    segment_id: str = 'segmentId'
    start_index: int = 'startIndex'
    end_index: int = Field('endIndex', default=0)


class NamedRange(Element):
    name_range_id: str = 'namedRangeId'
    name: str = 'name'
    range: ListOfElement(Range) = 'ranges'