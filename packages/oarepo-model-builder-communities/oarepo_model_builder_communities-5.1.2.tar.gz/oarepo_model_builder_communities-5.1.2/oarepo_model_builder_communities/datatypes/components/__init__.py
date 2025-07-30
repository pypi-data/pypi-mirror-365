from .communities_component import RecordCommunitiesComponent
from .communities_model import (
    CommunityMetadataModelComponent,
    RecordCommunitiesServiceModelComponent,
)
from .record_item import RecordCommunitiesItemModelComponent

RECORD_COMMUNITIES_COMPONENTS = [
    RecordCommunitiesServiceModelComponent,
    RecordCommunitiesComponent,
    CommunityMetadataModelComponent,
    RecordCommunitiesItemModelComponent
]
