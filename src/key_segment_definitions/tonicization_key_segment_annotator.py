""" Implementation of Clear Key Segment Definition 8 from thesis.
"""

from basic_key_segment_annotator import BasicKeySegmentAnnotator
from key_segment import KeySegment

class TonicizationKeySegmentAnnotator(BasicKeySegmentAnnotator):
    """ Implementation of Clear Key Segment Definition 8 from thesis,
    which defines a key segment as follows: "a maximal segment of music
    that does not contain tonicization events."
    """

    def get_key_segments(self):
        """ Get all key segments from current song that satisfy the criteria for
        Definition 8.
        """
        key_segments = []
        current_key_segment = None
        for rntxt_chord_idx, rntxt_chord in enumerate(self.rntxt_analysis):
            is_tonicization_chord = self.foreign_note_detector.check_if_is_tonicization_chord(rntxt_chord.figure)
            if is_tonicization_chord and current_key_segment:
                current_key_segment.set_offset_and_stop_measure_num_w_rntxt_chord(rntxt_chord)
                key_segments.append(current_key_segment)
                current_key_segment = None
            elif not is_tonicization_chord and current_key_segment is None:
                current_key_segment = KeySegment(first_rntxt_chord=rntxt_chord,
                                                 score_starts_on_measure_zero=self.score_starts_on_measure_zero,
                                                 rntxt_chords_start_idx=rntxt_chord_idx) 

        if current_key_segment:
            current_key_segment.set_offset_and_stop_measure_num(self.end_of_score_offset, self.last_measure_num)
            current_key_segment.set_rntxt_chords(self.rntxt_analysis, len(self.rntxt_analysis))
            key_segments.append(current_key_segment)

        return key_segments