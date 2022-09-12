""" Miscellaneous utility functions.
"""

import os
import re

import music21 as m21

def check_and_make_output_dir(filepath):
    """ Check if directory in `filepath` exists. If not,
    create it.

    Parameters
    ----------
    filepath : str
    """
    file_dir = os.path.dirname(filepath)
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)

def load_mxl_file_w_m21(mxl_filepath):
    """ Parse MusicXML file using music21.

    Parameters
    ----------
    mxl_filepath : str
    """
    parsed_mxl = m21.converter.parse(mxl_filepath)
    return parsed_mxl

def load_rntxt_file_w_m21(rntxt_filepath):
    """ Parse RomanText file using music21.

    Parameters
    ----------
    rntxt_filepath : str
    """
    rntxt_analysis = m21.converter.parse(rntxt_filepath, format='romanText')
    return rntxt_analysis.flat.getElementsByClass('RomanNumeral')

def load_filepaths_from_txt_file(txt_file_with_filepaths):
    """ Load filepaths from .txt file into a list.

    Parameters
    ----------
    txt_file_with_filepaths : str
    """
    with open(txt_file_with_filepaths) as text_file_with_filepaths:
        return [ filepath.strip() for filepath in text_file_with_filepaths ]

def strip_songname_from_path(song_filepath):
    """ Remove preceding path and filename extension to
    get isolated songname.

    Parameters
    ----------
    song_filepath : str
        Either ends in .csv, .mxl, or .txt
    """
    songname_w_extension = song_filepath.split('/')[-1]
    songname = songname_w_extension[:-4]
    return songname

def convert_camel_case_to_snake_case(camel_case_str):
    """ Convert a string written in camel case to snake case.

    Parameters
    ----------
    camel_case_str : str

    Notes
    -----
    This function is taken from
    https://stackoverflow.com/a/1176023
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_case_str).lower()