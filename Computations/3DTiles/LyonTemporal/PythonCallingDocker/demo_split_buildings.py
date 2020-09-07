import os
import sys
import logging
import shutil
from docker_split_buildings import DockerSplitBuilding
from demo import Demo
import demo_full_workflow as workflow


class DemoSplitBuildings(Demo):
    """
    A utility class gathering the conventional names, relative to this demo,
    used by the split buildings algorithm for designating its input/output 
    directories and filenames
    """
    def __init__(self):
        Demo.__init__(self)

    @staticmethod
    def derive_output_file_basename_from_input(input_filename):
        input_filename = os.path.basename(input_filename)
        input_no_extension = input_filename.rsplit('.', 1)[0]
        return input_no_extension + '_splited.gml'

    def get_vintage_borough_output_file_basename(self, vintage, borough):
        input_filename = self.input_demo.get_vintage_borough_output_filename(vintage, borough)
        return DemoSplitBuildings.derive_output_file_basename_from_input(input_filename)

    def get_resulting_filenames(self):
        """
        :return: the list of filenames (includes the directory name relative
                 to the invocation directory) that the split algorithm is
                 supposed to produce
        """
        result = list()
        for borough in self.boroughs:
            for vintage in self.vintages:
                result.append(self.get_vintage_borough_output_filename(vintage, borough))
        return result

    def run(self):
        input = self.get_input_demo()
        if not input.assert_output_files_exist():
            logging.error("Split misses some of its input files: exiting")
            sys.exit(1)
        self.get_output_dir(True)   # Create the output directory

        for borough in self.boroughs:
            for vintage in self.vintages:
                input_directory = input.get_vintage_borough_output_directory_name(vintage, borough)
                input_filename = input.get_vintage_borough_output_file_basename(vintage, borough)
                output_filename = self.get_vintage_borough_output_file_basename(vintage, borough)
                DockerSplitBuilding.split(
                    input_directory,
                    input_filename,
                    output_filename)
                logging.info(f'DemoSplitBuildings: citygml file {input_filename} was split.')
                # Because the split method doesn't know how to specify an output directory
                # (it this so hard?) by default it places its result side by side with the
                # input file. We thus need to move the resulting file
                output_dir = self.get_vintage_borough_output_directory_name(vintage,borough)
                if not os.path.isdir(output_dir):
                    os.mkdir(output_dir)
                shutil.move(os.path.join(input_directory, output_filename),
                            os.path.join(output_dir,output_filename))

if __name__ == '__main__': 
    split = workflow.demo_split

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=os.path.join(split.get_output_dir(True),
                                              'demo_split_buildings.log'),
                        filemode='w')
    logging.info("Starting to split files.")    

    split.run()
    split.assert_output_files_exist()
    logging.info("Resulting split files:")
    [ logging.info( "   " + file) for file in split.get_resulting_filenames() ]

