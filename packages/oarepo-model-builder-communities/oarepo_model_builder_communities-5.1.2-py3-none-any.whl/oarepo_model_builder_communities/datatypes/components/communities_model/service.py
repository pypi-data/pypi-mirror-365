from oarepo_model_builder.datatypes import ModelDataType
from oarepo_model_builder.datatypes.components import ServiceModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default


class RecordCommunitiesServiceModelComponent(ServiceModelComponent):
    eligible_datatypes = [ModelDataType]
    affects = [ServiceModelComponent]  # must be before workflow component

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "record":
            config = set_default(datatype, "service-config", {})
            config.setdefault("components", []).append(
                "{{oarepo_communities.services.components.default_workflow.CommunityDefaultWorkflowComponent}}"
            )
            config.setdefault("components", []).append(
                "{{oarepo_communities.services.components.include.CommunityInclusionComponent}}"
            )
            config.setdefault("components", []).append(
                "{{oarepo_communities.services.components.access.CommunityRecordAccessComponent}}"
            )
