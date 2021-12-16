import os
import re
import sys
import zipfile
import patch
import shutil
import logging
import wget
from pushd import pushd


class CityGMLFileFromArchive:
    def __init__(self, *args, **kwargs):
        # borough: the name of the borough to be retrieved
        self.borough = None
        # output_dir: designates the directory name where all the extracted content
        # will be placed.
        self.output_dir = None
        # pattern: one of "BATI", "TIN", "WATER" or "PONT"
        self.pattern = None
        # vintage: the year (as integer) at which the file corresponds to
        self.vintage = None

        self.__dict__.__init__(*args, **kwargs)

        # The name of the cityGML as it got extracted from the archive.
        # This member is only used when the cityGML file was miss-named in
        # the zip file: refer to prepare_archive_when_sanitize_needed().
        self.old_name = None
        # When needed the filename of the patch that should be applied.
        # This member is only used when the cityGML file is corrupted in
        # the zip file: refer to prepare_archive_when_sanitize_needed().
        self.patch_filename = None
        # Weather of not we should remove un-required/temporary files
        # (like the original archive) in the sake of disk space.
        self.tidy_up = False

        # Although the archive is spelled out the BATI string (which
        # stands for "constructed" in french) is holds a BATI cityGML
        # where BATI is here understood as building
        if not (
            self.pattern == "BATI"
            or self.pattern == "TIN"
            or self.pattern == "WATER"
            or self.pattern == "PONT"
        ):
            logging.info(f"Unknown pattern {self['pattern']}. Exiting")
            sys.exit(1)

        # The derived members, starting with the url reconstruction:
        repository = "https://download.data.grandlyon.com/files/grandlyon/" "imagerie/"
        # url: the url where to retrieve the archive from
        self.url = (
            repository
            + str(self.vintage)
            + "/maquette/"
            + self.borough
            + "_"
            + str(self.vintage)
            + ".zip"
        )
        # filename: the name of the cityGML file that this class retrieves and
        #       sanitizes
        self.file_name = (
            self.borough + "_" + self.pattern + "_" + str(self.vintage) + ".gml"
        )
        # key_name: the name used to identify the archive within the table of
        #     of possible renaming and patches that might need to be applied.
        self.key_name = self.borough + "_" + str(self.vintage)

    def create_output_directory(self):
        if not self.output_dir:
            logging.info("CityGMLFileFromArchive: unset output directory. Exiting.")
            sys.exit(1)
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

    def set_tidy_up(self):
        self.tidy_up = True

    def get_filename(self):
        return self.file_name

    def get_full_filename(self):
        """
        Fully qualified pathname for the file.
        """
        if not self.file_name:
            logging.info("CityGMLFileFromArchive: unset file_name. Exiting.")
            sys.exit(1)
        return os.path.join(self.output_dir, self.file_name)

    def assert_file_exists(self):
        full_filename = self.get_full_filename()
        if not os.path.isfile(full_filename):
            logging.info(f"Extracted file {full_filename} not found. Exiting.")
            sys.exit(1)
        return True

    def download_and_expand(self):
        with pushd(self.output_dir):
            # Because the server/network are sometimes flaky, giving many tries might
            # robustify the process:
            download_success = False
            number_max_wget_trial = 5
            seeked_url = self.url
            while not download_success:
                try:
                    wget.download(seeked_url)
                    download_success = True
                    logging.info(f"Download of {seeked_url} succeful.")
                except:
                    number_max_wget_trial -= 1
                    if number_max_wget_trial:
                        logging.info(f"Download of {seeked_url} failed: retying.")
                    else:
                        logging.info(f"Download of {seeked_url} failed: exiting.")
                        sys.exit(1)

            downloaded = os.path.basename(self.url)
            with zipfile.ZipFile(downloaded, "r") as zip_ref:
                for file in zip_ref.namelist():
                    if re.search(self.pattern, file):
                        zip_ref.extract(file)
            if self.tidy_up:
                os.remove(downloaded)
        logging.info(f"Archive {seeked_url} retrieved and unpacked.")

    def remove_wrapping_directory(self):
        """
        When some Lyon Metropole zip file get extracted its content
        ends up in a sub-directory. This methods strips this additionnal
        directory layer.
        """
        # Note that archive structure could be different for other data
        # repositories that build archives with another structural logic.
        extracted_subdir = os.path.join(
            self.output_dir, self.borough + "_" + str(self.vintage)
        )
        if not os.path.isdir(extracted_subdir):
            logging.info(f"Subdirectory {extracted_subdir} not found. Exiting.")
            sys.exit(1)
        files = os.listdir(extracted_subdir)
        for file in files:
            file_name = os.path.join(extracted_subdir, file)
            shutil.move(file_name, self.output_dir)
        os.rmdir(extracted_subdir)
        logging.info(f"Wrapping directory {extracted_subdir} removed.")

    def rename_when_needed(self):
        if not self.old_name:
            return
        if not self.file_name:
            logging.info("CityGMLFileFromArchive: unset name. Exiting.")
            sys.exit(1)
        old = os.path.join(self.output_dir, self.old_name)
        if not os.path.isfile(old):
            logging.info(f"File to rename {old} not found. Exiting")
            sys.exit(1)
        new = self.get_full_filename()
        os.rename(old, new)
        self.assert_file_exists()
        logging.info(f"Original file {old} properely renamed to {new}.")

    def patch_when_needed(self):
        if not self.patch_filename:
            return
        # Because patch files are relative (they refer to the file to which
        # the patch is applied by including this name in the patch), we first
        # need to copy the patch locally (i.e. in self.directory)
        source_patch = self.patch_filename
        if not os.path.isfile(source_patch):
            logging.info(f"Patch file {source_patch} not found. Exiting")
            sys.exit(1)
        target_patch_file = os.path.join(
            self.output_dir, os.path.basename(self.patch_filename)
        )
        shutil.copyfile(source_patch, target_patch_file)
        patch_file = os.path.basename(source_patch)
        with pushd(self.output_dir):
            try:
                success = patch.fromfile(patch_file).apply()
            except:
                success = False
            if not success:
                logging.info(f"Patch failed for {source_patch}. Exiting")
                sys.exit(1)
        logging.info(f"Patch succeeded for {source_patch}.")

    def prepare_archive_when_sanitize_needed(self):
        """
        Sanitizing archive files is the exception.
        """
        # FIXME: The following hard-wiring is a weakness
        patches_directory = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "DataPatches"
        )

        # Vintage 2009
        if self.key_name == "LYON_4EME_2009":
            self.old_name = "LYON_4_BATI_2009.gml"
        if self.key_name == "LYON_5EME_2009":
            self.old_name = "LYON_5_BATI_2009.gml"
        if self.key_name == "LYON_7EME_2009":
            self.patch_filename = os.path.join(
                patches_directory,
                "LYON_7EME_BATI_2009.gml.patch",
            )
        if self.key_name == "LYON_8EME_2009":
            self.patch_filename = os.path.join(
                patches_directory,
                "LYON_8EME_BATI_2009.gml.patch",
            )
        # Vintage 2012
        if self.key_name == "LYON_7EME_2012":
            self.patch_filename = os.path.join(
                patches_directory,
                "LYON_7EME_BATI_2012.gml.patch",
            )
        if self.key_name == "LYON_8EME_2012":
            self.patch_filename = os.path.join(
                patches_directory,
                "LYON_8EME_BATI_2012.gml.patch",
            )

        # Vintage 2015
        if self.key_name == "LYON_7EME_2015":
            self.old_name = "LYON_7_BATI_2015.gml"

    def extract(self):
        self.create_output_directory()
        self.prepare_archive_when_sanitize_needed()
        self.download_and_expand()
        # Removing the wrapping directory must be done before renaming and
        # applying patches for things to work (that is find files where
        # expected)
        self.remove_wrapping_directory()
        self.rename_when_needed()
        self.patch_when_needed()
        self.assert_file_exists()
        logging.info(f"Extraction of {self.file_name} done.")
