from oarepo_model_builder.builders import OutputBuilder
from oarepo_model_builder.outputs.cfg import CFGOutput


class CommunitiesSetupCfgBuilder(OutputBuilder):
    TYPE = "communities_setup_cfg"

    def finish(self):
        super().finish()

        output: CFGOutput = self.builder.get_output("cfg", "setup.cfg")

        output.add_dependency("oarepo-communities", ">=5.0.0")
        output.add_dependency("oarepo-global-search", ">=1.0.20")
