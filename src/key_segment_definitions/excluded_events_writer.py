""" Output the clear key segments to an Npz file in the
format of a list of eighth note beats (i.e. events), where
each event either has value 0 or 1. 0 indicates that the
event is part of a clear key segment, while 1 indicates that
it is not part of any segment (i.e. it is ambiguous in terms
of key).
"""

import numpy as np

from file_handlers import NpzFileHandler
from utils import convert_camel_case_to_snake_case, strip_songname_from_path

NO_EXCLUDED_EVENT = 0

class ExcludedEventsWriter:
    """ Output the clear key segments to an Npz file in the
    format of a list of eighth note beats (i.e. events), where
    each event either has value 0 or 1. 0 indicates that the
    event is part of a clear key segment, while 1 indicates that
    it is not part of any segment (i.e. it is ambiguous in terms
    of key).
    """

    def __init__(self, key_segment_annotator_class, ground_truth_key_labels_npz_path, micchi_predictions=False,
                 allow_root_position_viio_chords=False):
        """

        Parameters
        ----------
        key_segment_annotator_class : str
        ground_truth_key_labels_npz_path : str
        micchi_predictions : bool
            If true, clear key segments were determined by the Frog model's key
            and chord predictions. If false, ground truth key/chord labels were
            used to create the clear key segments.
        allow_root_position_viio_chords : bool
        """
        self.songs_to_excluded_events_dict = {}

        self.npz_filehandler = NpzFileHandler()
        self.ground_truth_key_labels_dict = self.npz_filehandler.read_npz_file(ground_truth_key_labels_npz_path)

        self.micchi_predictions = micchi_predictions
        key_segment_annotator_class = convert_camel_case_to_snake_case(key_segment_annotator_class)
        self.output_npz_filename = self.get_output_npz_filename(key_segment_annotator_class,
                                                                allow_root_position_viio_chords)

    def get_output_npz_filename(self, key_segment_annotator_class, allow_root_position_viio_chords):
        """ Get the name of the outputted Npz file.

        Parameters
        ----------
        key_segment_annotator_class : str
        allow_root_position_viio_chords : bool
        """
        output_npz_filename = "out/micchi2021_"

        if self.micchi_predictions:
            output_npz_filename += "predicted_"
            
        output_npz_filename += key_segment_annotator_class

        if allow_root_position_viio_chords:
            output_npz_filename += "_allow_root_pos_viio"

        output_npz_filename += "_validation_excluded_events.npz"

        return output_npz_filename

    def get_excluded_events_for_song(self, key_segments, mxl_filepath):
        """ For each song, create a list with length equal to the number of eighth note beats
        in the song. Each eighth note beat either has a value of 0 or 1: 0 if the eighth note
        event is part of a clear key segment and 1 if it is ambiguous (i.e. not part of any
        clear key segment).

        Parameters
        ----------
        key_segments : list of KeySegment
        mxl_filepath : str
        """
        songname = strip_songname_from_path(mxl_filepath)
        
        song_excluded_events = np.ones_like(self.ground_truth_key_labels_dict[songname])

        for key_segment in key_segments:
            key_segment_onset_eighth_note_idx = self.convert_onset_to_eighth_note_beat_idx(key_segment.onset)
            key_segment_offset_eighth_note_idx = self.convert_onset_to_eighth_note_beat_idx(key_segment.offset)
            song_excluded_events[key_segment_onset_eighth_note_idx:key_segment_offset_eighth_note_idx] = NO_EXCLUDED_EVENT

        self.songs_to_excluded_events_dict[songname] = song_excluded_events

    def convert_onset_to_eighth_note_beat_idx(self, onset):
        """ Convert onset in quarters to eighth note beat index.

        Parameters
        ----------
        onset : float
        """
        return int(onset // 0.5)

    def write_songs_to_excluded_events_dict_to_npz_file(self):
        """ Output excluded events for all songs to an Npz file.
        """
        self.npz_filehandler.write_content_to_npz_file(self.songs_to_excluded_events_dict,
                                                       self.output_npz_filename)