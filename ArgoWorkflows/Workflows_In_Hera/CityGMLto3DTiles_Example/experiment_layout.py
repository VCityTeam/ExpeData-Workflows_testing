import os
import types


class layout:
    def __init__(self, constants) -> None:
        self.experiment_output_dir = constants.experiment_output_dir
        self.pattern = constants.pattern

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
        return borough + "_" + self.pattern + "_" + vintage + "_split.gml"

    def split_buildings_output_absolute_filename(self, vintage, borough):
        return os.path.join(
            self.split_buildings_output_dir(vintage, borough),
            self.split_buildings_output_filename(self, vintage, borough),
        )

    ###### stage 3
    def strip_gml_output_dir(self, vintage, borough):
        return os.path.join(
            self.stage_output_dir("stage_3"),
            vintage,
            borough + "_" + vintage,
        )

    def strip_gml_output_filename(self, vintage, borough):
        return borough + "_" + self.pattern + "_" + vintage + "_stripped.gml"

    def strip_gml_output_absolute_filename(self, vintage, borough):
        return os.path.join(
            self.strip_gml_output_dir(vintage, borough),
            self.strip_gml_output_filename(vintage, borough),
        )

    ##### Utils (fake @staticmethods)
    # DESIGN NOTES: strictly speaking the following methods are @staticmethod
    # (they do not use any instnace attributes). Yet in order to avoid passing
    # e.g. three arguments
    #   1. layout (as a class)
    #   2. an instance (layout(constants)) or just the constructor argument
    #      that is some constants
    #   3. a database instance (layout.database(vintage)) or just/equivalently
    #      a vintage value
    # if suffice to pass
    #   1. layout_instance = layout(constants) that is an instance of the class
    #   2. vintage (that enables to build) database = layout_instance(vintage)
    def container_name_postend(unused_self, vintage, borough):
        """Hera Tasks need to have distinguished named. When looping we thus
        need to generated task names by declining a task radical (e.g. collect,
        strip, split) with parameter (vintage, borough) dependent names.

        Returns:
            str: an AW compatible (part of a) task name declined out of
            the argument parameters.
        """
        return str(vintage) + "-" + borough.replace("_", "-")

    def database(unused_self, vintage=None):
        if vintage:
            name = "citydb-lyon-" + str(vintage)
        else:
            name = "no-vingage-given-dummy-db-name"
        return types.SimpleNamespace(
            port="5432",
            name=name,
            user="postgres",
            password="postgres",
            keep_database=True,
        )
