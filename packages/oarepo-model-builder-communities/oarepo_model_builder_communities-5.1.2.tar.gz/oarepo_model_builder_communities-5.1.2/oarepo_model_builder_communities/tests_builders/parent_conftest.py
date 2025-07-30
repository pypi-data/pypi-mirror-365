from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class CommunitiesConftestBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "communities_conftest"
    template = "communities-conftest"

    def _get_output_module(self):
        return (
            f'{self.current_model.definition["tests"]["module"]}.communities.conftest'
        )

    def finish(self, **extra_kwargs):
        tests = getattr(self.current_model, "section_tests")
        super().finish(
            fixtures=tests.fixtures,
            test_constants=tests.constants,
            published_record=self.current_model.published_record,
            **extra_kwargs,
        )
