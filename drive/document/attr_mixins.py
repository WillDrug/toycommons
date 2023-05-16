from .json_dataclass import Field


class Suggested:
    suggested_insertions: str = 'suggestedInsertionIds'
    suggested_deletions: str = 'suggestedDeletionIds'
    suggested_text_style: dict = 'suggestedTextStyleChanges'
    suggested_style: str = Field('suggestedTableRowStyleChanges', alt_names=('suggestedTableCellStyleChanges',
                                                                             'suggestedTextStyleChanges',
                                                                             'suggestedParagraphStyleChanges'))
    suggested_bullet: str = 'suggestedBulletChanges'
    suggested_positions: list = 'suggestedPositionedObjectIds'
    suggested_properties: str = Field('suggestedPositionedObjectPropertiesChanges',
                                      alt_names=('suggestedInlineObjectPropertiesChanges',
                                                 'suggestedListPropertiesChanges'))
