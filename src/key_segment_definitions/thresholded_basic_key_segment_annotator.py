""" Implementation of thresholded version of Clear Key Segment
Definition 1 from thesis.
"""

from basic_key_segment_annotator import BasicKeySegmentAnnotator
from foreign_note_detector import ForeignNoteDetector
from key_segment import KeySegment

class ThresholdedBasicKeySegmentAnnotator(BasicKeySegmentAnnotator):
    """ Implementation of thresholded version of Clear Key Segment
    Definition 1 from thesis.
    Checks for the following criteria when detecting key segments:
    1. The key segment begins on a I or V chord.
    2. It contains a V to I progression.
    3. It ends on a I or V chord.
    4. Any non-scale note is a figuration.

    Also serves as the base class for the implementation of the other
    thresholded Clear Key Segment Definitions.
    """

    def __init__(self, parsed_mxl, rntxt_analysis, measure_onset_finder,
                 thresholded_key_segment_indices, **kwargs):
        """

        Parameters
        ----------
        parsed_mxl : music21.stream.Score
            Parsed Music21 score for an entire song.
        rntxt_analysis : music21.stream.iterator.RecursiveIterator 
            RomanText chords for the entire song.
        measure_onset_finder : MeasureOnsetFinder
            Used to find the index associated with the last measure in the song.
        thresholded_key_segment_indices : list of [int, int]
        min_key_segment_quarter_length : int
            The minimum length a key segment should be in quarter note duration.
        """
        self.rntxt_analysis = rntxt_analysis

        if rntxt_analysis[0].offset != 0.0:
            print("Warning: `rntxt_analysis[0].offset` starts on {}, not 0.0".format(rntxt_analysis[0].offset))

        self.score_starts_on_measure_zero = True if rntxt_analysis[0].measureNumber == 0 else False

        self.end_of_score_offset = parsed_mxl.duration.quarterLength
        self.last_measure_num = measure_onset_finder.last_measure_num

        if "min_key_segment_quarter_length" in kwargs:
            self.min_key_segment_quarter_length = kwargs["min_key_segment_quarter_length"]

        self.foreign_note_detector = ForeignNoteDetector()

        self.thresholded_key_segments = self.get_key_segments_from_key_segment_indices(thresholded_key_segment_indices)

    def get_key_segments_from_key_segment_indices(self, key_segment_indices):
        """ Create key segment objects using the eighth note beat start and
        stop times of each key segment specified in `key_segment_indices`.
        The start/stop times given in `key_segment_indices` are for the
        thresholded key segments.

        Parameters
        ----------
        key_segment_indices : list of [int, int]
        """
        key_segments = []
        for key_segment_idx in key_segment_indices:
            start_eighth_note_beat_idx, stop_eighth_note_beat_idx = key_segment_idx[0], key_segment_idx[1]
            key_segment_start_onset = self.convert_eighth_note_beat_idx_to_onset(start_eighth_note_beat_idx)
            start_rntxt_chord, start_rntxt_chord_idx = self.get_start_rntxt_chord_and_idx(key_segment_start_onset)
            key_segment_stop_offset = self.convert_eighth_note_beat_idx_to_onset(stop_eighth_note_beat_idx)
            stop_rntxt_chord_idx = self.get_stop_rntxt_chord_idx(key_segment_stop_offset)
            key_segment = KeySegment(key_name=start_rntxt_chord.key.tonicPitchNameWithCase,
                                     onset=key_segment_start_onset, offset=key_segment_stop_offset,
                                     start_measure_num=start_rntxt_chord.measureNumber,
                                     score_starts_on_measure_zero=self.score_starts_on_measure_zero,
                                     rntxt_chords_start_idx=start_rntxt_chord_idx,
                                     rntxt_chords=self.rntxt_analysis[start_rntxt_chord_idx:stop_rntxt_chord_idx])
            key_segments.append(key_segment)

        return key_segments

    def get_start_rntxt_chord_and_idx(self, key_segment_start_onset):
        """ Using the onset time of the current key segment in quarters,
        find the first RomanText chord that occurs in this key segment,
        as well as the index of this RomanText chord.

        Parameters
        ----------
        key_segment_start_onset : float
        """
        prev_rntxt_chord = self.rntxt_analysis[0]
        start_rntxt_chord = None
        start_rntxt_chord_idx = 0
        for idx, rntxt_chord in enumerate(self.rntxt_analysis[1:]):
            current_rntxt_chord_idx = (idx + 1)
            if rntxt_chord.offset > key_segment_start_onset:
                start_rntxt_chord = prev_rntxt_chord
                start_rntxt_chord_idx = current_rntxt_chord_idx - 1
                break
            prev_rntxt_chord = rntxt_chord

        if start_rntxt_chord is None:
            start_rntxt_chord = self.rntxt_analysis[-1]
            start_rntxt_chord_idx = len(self.rntxt_analysis) - 1

        return start_rntxt_chord, start_rntxt_chord_idx

    def get_stop_rntxt_chord_idx(self, key_segment_stop_offset):
        """ Using the offset time of the current key segment in quarters,
        find the index of the first RomanText chord that occurs immediately
        after the current key segment. 

        Parameters
        ----------
        key_segment_stop_offset : float
        """
        stop_rntxt_chord_idx = None 
        for idx, rntxt_chord in enumerate(self.rntxt_analysis[1:]):
            current_rntxt_chord_idx = (idx + 1)
            if rntxt_chord.offset >= key_segment_stop_offset:
                stop_rntxt_chord_idx = current_rntxt_chord_idx
                break

        if stop_rntxt_chord_idx is None:
            stop_rntxt_chord_idx = len(self.rntxt_analysis)

        return stop_rntxt_chord_idx

    def convert_eighth_note_beat_idx_to_onset(self, eighth_note_beat_idx):
        """ Convert eighth note beat index to onset time in quarter notes.

        Parameters
        ----------
        eighth_note_beat_idx : int
        """
        return eighth_note_beat_idx / 2 

    def get_key_segments(self):
        """ Get all clear thresholded key segments from current song that satisfy
        the criteria for Definition 1.
        """
        key_segments_wo_foreign_notes = self.foreign_note_detector.find_foreign_notes_and_split_key_segments_accordingly(self.thresholded_key_segments)
        trimmed_key_segments = self.trim_key_segments_to_start_and_end_on_allowable_chords(key_segments_wo_foreign_notes)
        key_segments_w_V_to_I_progs = self.remove_key_segments_without_V_to_I_progression(trimmed_key_segments)

        if self.min_key_segment_quarter_length:
            key_segments_w_V_to_I_progs = self.remove_key_segments_shorter_than_min_length(key_segments_w_V_to_I_progs)

        return key_segments_w_V_to_I_progs