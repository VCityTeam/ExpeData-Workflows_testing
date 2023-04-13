import os

class layout():

  ###### stage 2
  def split_buildings_input_filename(parameters):
    # FIXME this encapsulates a (layout) knowledge that belongs to the previous
    # FIXME task and that should thus not be expressed here.
    return os.path.join(
              parameters.experiment_output_dir,
              "stage_1",
              parameters.vintage,
              parameters.borough + "_" + parameters.vintage,
              parameters.borough
              + "_"
              + parameters.pattern
              + "_"
              + parameters.vintage
              + ".gml",
          )
  def split_buildings_output_dir(parameters):
    return os.path.join(
              parameters.experiment_output_dir,
              "stage_2",
              parameters.vintage,
              parameters.borough + "_" + parameters.vintage,
          )

  def split_buildings_output_filename(parameters):
    return (
      parameters.borough
      + "_"
      + parameters.pattern
      + "_"
      + parameters.vintage
      + "_split.gml"
      )

  ###### stage 3
  def strip_gml_output_dir(parameters):
    return os.path.join(
              parameters.experiment_output_dir,
              "stage_3",
              parameters.vintage,
              parameters.borough + "_" + parameters.vintage,
    )

  def strip_gml_output_filename(parameters):
    return (
      parameters.borough
      + "_"
      + parameters.pattern
      + "_"
      + parameters.vintage
      + "_stripped.gml"
      )