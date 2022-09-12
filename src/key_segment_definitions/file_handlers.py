""" Read and write Npz and JSON files.
"""
import json
import os

import numpy as np

class FileHandler:
    """ File handler base class.
    """

    def check_and_make_output_dir(self, filepath):
        """ Check if directory in `filepath` exists. If not,
        create it.

        Parameters
        ----------
        filepath : str
        """
        filepath_dir = os.path.dirname(filepath)
        if not os.path.isdir(filepath_dir):
            os.mkdir(filepath_dir)

class NpzFileHandler(FileHandler):
    """ Reads/writes Npz files.
    """

    def read_npz_file(self, npz_filepath):
        """ Read Npz file.

        Parameters
        ----------
        npz_filepath : str
        """
        return dict(np.load(npz_filepath))

    def write_content_to_npz_file(self, file_content_dict, npz_filepath):
        """ Write content to Npz file.

        Parameters
        ----------
        file_content_dict : dict { str : np.ndarray }
        npz_filepath : str
        """
        self.check_and_make_output_dir(npz_filepath)

        with open(npz_filepath, 'wb') as npz_file:
            np.savez(npz_file, **file_content_dict)

class JsonFileHandler(FileHandler):
    """ Reads/writes JSON files.
    """

    def write_content_to_json_file(self, file_content_dict, json_filepath):
        """ Write content to JSON file.

        Parameters
        ----------
        file_content_dict : dict { str : str }
        json_filepath : str
        """
        self.check_and_make_output_dir(json_filepath)

        json_file_content = json.dumps(file_content_dict)

        with open(json_filepath, 'w') as json_file:
            json_file.write(json_file_content)