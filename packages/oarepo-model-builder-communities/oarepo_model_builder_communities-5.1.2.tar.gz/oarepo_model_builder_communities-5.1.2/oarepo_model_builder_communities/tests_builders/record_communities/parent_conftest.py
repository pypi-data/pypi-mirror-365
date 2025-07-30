from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class RecordCommunitiesParentConftestBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "record_communities_parent_conftest"
    template = "record-communities-parent-conftest"

    def _get_output_module(self):
        return f'{self.current_model.definition["tests"]["module"]}.conftest'
