import os


class layout:
    def __init__(self, inputs) -> None:
        self.experiment_output_dir = inputs.constants.experiment_output_dir
        self.pattern = inputs.constants.pattern

    def stage_output_dir(self, stage_output_dir):
        return os.path.join(self.experiment_output_dir, stage_output_dir)

    ###### stage 1
    def collect_output_dir(self, vintage, borough):
        return os.path.join(
            self.stage_output_dir("stage_1"),
            vintage,
            borough + "_" + vintage,
        )

    def collect_output_filename(self, vintage, borough):
        return os.path.join(
            self.collect_output_dir(vintage, borough),
            borough + "_" + self.pattern + "_" + vintage + ".gml",
        )

    ###### stage 2
    def split_buildings_input_filename(self, vintage, borough):
        return self.collect_output_filename(vintage, borough)

    def split_buildings_output_dir(self, vintage, borough):
        return os.path.join(
            self.stage_output_dir("stage_2"),
            vintage,
            borough + "_" + vintage,
        )

    def split_buildings_output_filename(self, vintage, borough):
        return os.path.join(
            self.split_buildings_output_dir(vintage, borough),
            borough + "_" + self.pattern + "_" + vintage + "_split.gml",
        )

    ###### stage 3
    def strip_gml_output_dir(self, vintage, borough):
        return os.path.join(
            self.stage_output_dir("stage_3"),
            vintage,
            borough + "_" + vintage,
        )

    def strip_gml_output_filename(self, vintage, borough):
        return os.path.join(
            self.strip_gml_output_dir(vintage, borough),
            borough + "_" + self.pattern + "_" + vintage + "_stripped.gml",
        )
