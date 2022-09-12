"""" Implementation of thresholded version of Clear Key Segment
Definition 4 from thesis.
"""

from foreign_note_detector import ForeignNoteDetector
from thresholded_relaxed_key_segment_annotator import ThresholdedRelaxedKeySegmentAnnotator

class ThresholdedChromaticKeySegmentAnnotator(ThresholdedRelaxedKeySegmentAnnotator):
    """ Implementation of thresholded version of Clear Key Segment
    Definition 4 from thesis.
    Checks for the following criteria when detecting key segments:
    1. It begins on a tonic chord or dominant harmony.
    2. It contains a progression from dominant harmony to a tonic chord.
    3. It ends on a tonic or dominant harmony.
    4. Any non-scale note is a figuration or part of a mode mixture,
       a Neapolitan chord, or an augmented 6th chord.
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
        self.inverted_chord_regex = "(732|742|765|6432|643|642|654|65|6/5|64|6/4|63|6/3|62|6|532|54|5|43|4/3|42|4/2|4|3|2)"

        self.rntxt_analysis = rntxt_analysis

        if rntxt_analysis[0].offset != 0.0:
            print("Warning: `rntxt_analysis[0].offset` starts on {}, not 0.0".format(rntxt_analysis[0].offset))

        self.score_starts_on_measure_zero = True if rntxt_analysis[0].measureNumber == 0 else False

        self.end_of_score_offset = parsed_mxl.duration.quarterLength
        self.last_measure_num = measure_onset_finder.last_measure_num

        if "min_key_segment_quarter_length" in kwargs:
            self.min_key_segment_quarter_length = kwargs["min_key_segment_quarter_length"]

        self.allow_root_position_viio_chords = True

        self.foreign_note_detector = ForeignNoteDetector(allow_for_mixture=True, allow_aug6_chords=True,
                                                         allow_neapolitan_chords=True)

        self.thresholded_key_segments = self.get_key_segments_from_key_segment_indices(thresholded_key_segment_indices)