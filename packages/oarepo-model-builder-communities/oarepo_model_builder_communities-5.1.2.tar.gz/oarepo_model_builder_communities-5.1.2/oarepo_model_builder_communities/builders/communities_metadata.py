from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class CommunitiesMetadataBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "communities_metadata"
    section = "communities-metadata"
    template = "communities-metadata"

    def finish(self, **extra_kwargs):
        super().finish(
            published_record=self.current_model.published_record, **extra_kwargs
        )
