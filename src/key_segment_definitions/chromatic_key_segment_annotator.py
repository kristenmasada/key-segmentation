"""
"""

from relaxed_key_segment_annotator import RelaxedKeySegmentAnnotator

from foreign_note_detector import ForeignNoteDetector

class ChromaticKeySegmentAnnotator(RelaxedKeySegmentAnnotator):
    """
    """

    def __init__(self, parsed_mxl, rntxt_analysis, measure_onset_finder,
                 **kwargs):
        """
        """
        self.inverted_chord_regex = "(732|742|765|6432|643|642|654|65|6/5|64|6/4|63|6/3|62|6|532|54|5|43|4/3|42|4/2|4|3|2)"

        self.rntxt_analysis = rntxt_analysis

        if rntxt_analysis[0].offset != 0.0:
            print("Warning: `rntxt_analysis[0].offset` starts on {}, not 0.0".format(rntxt_analysis[0].offset))

        self.score_starts_on_measure_zero = True if rntxt_analysis[0].measureNumber == 0 else False

        self.end_of_score_offset = parsed_mxl.duration.quarterLength
        self.last_measure_num = measure_onset_finder.last_measure_num

        if "min_key_segment_quarter_length" in kwargs:
            self.min_key_segment_quarter_length = kwargs["min_key_segment_quarter_length"]

        if "allow_root_position_viio_chords" in kwargs:
            self.allow_root_position_viio_chords = kwargs["allow_root_position_viio_chords"]
        else:
            self.allow_root_position_viio_chords = False

        self.foreign_note_detector = ForeignNoteDetector(allow_for_mixture=True, allow_aug6_chords=True,
                                                         allow_neapolitan_chords=True)