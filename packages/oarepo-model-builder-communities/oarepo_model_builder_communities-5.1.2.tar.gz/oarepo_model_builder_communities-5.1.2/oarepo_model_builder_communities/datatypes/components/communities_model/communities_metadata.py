import marshmallow as ma
from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components.model.record_metadata import (
    RecordMetadataClassSchema,
    RecordMetadataModelComponent,
)
from oarepo_model_builder.datatypes.components.model.utils import set_default


class CommunityMetadataModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [RecordMetadataModelComponent]

    class ModelSchema(ma.Schema):
        record_metadata = ma.fields.Nested(
            RecordMetadataClassSchema,
            attribute="communities-metadata",
            data_key="communities-metadata",
            metadata={"doc": "Communities realtion metadata settings"},
        )

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "draft":
            metadata = set_default(datatype, "communities-metadata", {})
            prefix = context["published_record"].definition["module"]["prefix"]
            metadata_module = metadata.setdefault(
                "module",
                datatype.definition["record-metadata"]["module"],
            )
            metadata.setdefault("generate", True)
            metadata.setdefault(
                "class", f"{metadata_module}.{prefix}CommunitiesMetadata"
            )
            metadata.setdefault(
                "base-classes",
                [
                    "invenio_db.db{db.Model}",
                    "invenio_communities.records.records.models.CommunityRelationMixin",
                ],
            )
            metadata.setdefault("imports", [])
            metadata.setdefault(
                "table",
                f"{context['published_record'].definition['module']['prefix-snake']}_communities_metadata",
            )
