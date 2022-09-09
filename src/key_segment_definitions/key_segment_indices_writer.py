"""
"""

import numpy as np

from file_handlers import NpzFileHandler
from utils import convert_camel_case_to_snake_case, strip_songname_from_path

class KeySegmentIndicesWriter:

    def __init__(self, key_segment_annotator_class, micchi_predictions=False,
                 allow_root_position_viio_chords=False, thresholded=False):
        """

        Parameters
        ----------
        key_segment_annotator_class : str
        micchi_predictions : bool
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

    def get_output_npz_filename(self, key_segment_annotator_class, micchi_predictions, allow_root_position_viio_chords,
                                thresholded=False):
        """

        Parameters
        ----------
        key_segment_annotator_class : str
        micchi_predictions : bool
        allow_root_position_viio_chords : bool
        thresholded : bool
        """
        output_npz_filename = "out/"

        if thresholded:
            output_npz_filename += "thresholded_"
        
        output_npz_filename += "micchi2021_"

        if micchi_predictions:
            output_npz_filename += "predicted_"
            
        output_npz_filename += key_segment_annotator_class

        if allow_root_position_viio_chords:
            output_npz_filename += "_allow_root_pos_viio"

        output_npz_filename += "_validation_key_segment_indices.npz"

        return output_npz_filename

    def get_key_segment_indices_for_song(self, key_segments, mxl_filepath):
        """
        """
        songname = strip_songname_from_path(mxl_filepath)
        
        song_key_segment_indices = []

        for key_segment in key_segments:
            key_segment_onset_eighth_note_idx = self.convert_onset_to_eighth_note_beat_idx(key_segment.onset)
            key_segment_offset_eighth_note_idx = self.convert_onset_to_eighth_note_beat_idx(key_segment.offset)
            song_key_segment_indices.append((key_segment_onset_eighth_note_idx, key_segment_offset_eighth_note_idx))

        self.songs_to_key_segment_indices_dict[songname] = np.asarray(song_key_segment_indices)

    def convert_onset_to_eighth_note_beat_idx(self, onset):
        """
        """
        return int(onset // 0.5)

    def write_songs_to_key_segment_indices_dict_to_npz_file(self):
        """
        """
        self.npz_filehandler.write_content_to_npz_file(self.songs_to_key_segment_indices_dict,
                                                       self.output_npz_filename)