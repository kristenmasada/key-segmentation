""" Output the clear key segments to an Npz file in the
format of a list of eighth note beat indices indicating
the start and stop time of each key segment (NOTE: stop
index is exclusive).
"""

import numpy as np

from file_handlers import NpzFileHandler
from utils import convert_camel_case_to_snake_case, \
                  key_segment_annotator_class_to_def, \
                  strip_songname_from_path

class KeySegmentIndicesWriter:
    """ Output the clear key segments to an Npz file in the
    format of a list of eighth note beat indices indicating
    the start and stop time of each key segment (NOTE: stop
    index is exclusive).
    """

    def __init__(self, key_segment_annotator_class, micchi_predictions=False,
                 allow_root_position_viio_chords=False, thresholded=False):
        """

        Parameters
        ----------
        key_segment_annotator_class : str
        micchi_predictions : bool
            If true, clear key segments were determined by the Frog model's key
            and chord predictions. If false, ground truth key/chord labels were
            used to create the clear key segments.
        allow_root_position_viio_chords : bool
        thresholded : bool
        """
        self.songs_to_key_segment_indices_dict = {}

        self.npz_filehandler = NpzFileHandler()

        key_segment_annotator_class = convert_camel_case_to_snake_case(key_segment_annotator_class)
        self.output_npz_filename = self.get_output_npz_filename(key_segment_annotator_class,
                                                                micchi_predictions,
                                                                allow_root_position_viio_chords,
                                                                thresholded)

    def get_output_npz_filename(self, key_segment_annotator_class, micchi_predictions,
                                allow_root_position_viio_chords, thresholded=False):
        """ Get the name of the outputted Npz file.

        Parameters
        ----------
        key_segment_annotator_class : str
        micchi_predictions : bool
        allow_root_position_viio_chords : bool
        thresholded : bool
        """
        output_npz_filename = "out/meta-corpus_validation_"

        if thresholded:
            output_npz_filename += "thresholded_pred_"
        elif micchi_predictions:
            output_npz_filename += "pred_"
        else:
            output_npz_filename += "ground_truth_"

        output_npz_filename += "key_segment_boundaries_"

        output_npz_filename += key_segment_annotator_class_to_def[key_segment_annotator_class]

        if allow_root_position_viio_chords:
            output_npz_filename += "v2"

        output_npz_filename += ".npz"

        return output_npz_filename

    def get_key_segment_indices_for_song(self, key_segments, mxl_filepath):
        """ For each clear key segment in a song, add the eighth note beat
        index start time and end time of each key segment to a list.

        Parameters
        ----------
        key_segments : list of KeySegment
        mxl_filepath : str
        """
        songname = strip_songname_from_path(mxl_filepath)

        song_key_segment_indices = []

        for key_segment in key_segments:
            key_segment_onset_eighth_note_idx = self.convert_onset_to_eighth_note_beat_idx(key_segment.onset)
            key_segment_offset_eighth_note_idx = self.convert_onset_to_eighth_note_beat_idx(key_segment.offset)
            song_key_segment_indices.append((key_segment_onset_eighth_note_idx, key_segment_offset_eighth_note_idx))

        self.songs_to_key_segment_indices_dict[songname] = np.asarray(song_key_segment_indices)

    def convert_onset_to_eighth_note_beat_idx(self, onset):
        """ Convert onset in quarters to eighth note beat index.

        Parameters
        ----------
        onset : float
        """
        return int(onset // 0.5)

    def write_songs_to_key_segment_indices_dict_to_npz_file(self):
        """ Output key segment indices for all songs to an Npz file.
        """
        self.npz_filehandler.write_content_to_npz_file(self.songs_to_key_segment_indices_dict,
                                                       self.output_npz_filename)