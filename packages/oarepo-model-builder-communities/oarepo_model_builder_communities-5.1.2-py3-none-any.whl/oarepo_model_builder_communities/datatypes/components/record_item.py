from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType, Section
from oarepo_model_builder.datatypes.components import DefaultsModelComponent
from oarepo_model_builder.datatypes.model import Link
from oarepo_model_builder.utils.python_name import Import
from oarepo_model_builder.datatypes.components import RecordItemModelComponent

class RecordCommunitiesItemModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [RecordItemModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        record_item_config = datatype.definition["record-item"]
        record_item_config.setdefault("components", []).append("{{oarepo_communities.services.results.RecordCommunitiesComponent}}()")



