""" Implementation of thresholded version of Clear Key
Segment Definition 3 from thesis.
"""

import re

from thresholded_basic_key_segment_annotator import ThresholdedBasicKeySegmentAnnotator

class ThresholdedRelaxedKeySegmentAnnotator(ThresholdedBasicKeySegmentAnnotator):
    """ Implementation of thresholded version of Clear Key Segment
    Definition 3 from thesis.
    Checks for the following criteria when detecting key segments:
    1. It begins on a tonic chord or dominant harmony. 
    2. It contains a progression from dominant harmony to a tonic chord.
    3. It ends on a tonic or dominant harmony.
    4. Any non-scale note is a figuration.
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
        self.allow_root_position_viio_chords = True

        self.inverted_chord_regex = "(732|742|765|6432|643|642|654|65|6/5|64|6/4|63|6/3|62|6|532|54|5|43|4/3|42|4/2|4|3|2)"
        
        super().__init__(parsed_mxl, rntxt_analysis, measure_onset_finder,
                         thresholded_key_segment_indices, **kwargs)

    def remove_key_segments_without_V_to_I_progression(self, key_segments):
        """ Remove any key segments that do not contain a progression
        from dominant harmony (i.e. V or VII) to a I chord.

        Parameters
        ----------
        key_segments : list of KeySegment
        """
        key_segments_w_dom_harm_to_I_progs = []
        for key_segment in key_segments:
            dominant_harmony_seen = False
            for rntxt_chord in key_segment.rntxt_chords:
                if dominant_harmony_seen and self.check_if_rntxt_chord_is_I_chord(rntxt_chord):
                    key_segments_w_dom_harm_to_I_progs.append(key_segment)
                    break
                elif self.check_if_rntxt_chord_is_V_or_VII_chord(rntxt_chord):
                    dominant_harmony_seen = True

        return key_segments_w_dom_harm_to_I_progs

    def check_if_rntxt_chord_is_V_or_VII_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is part of dominant
        harmony (i.e. a V or VII chord). If the user has specified
        that root position VII chords should not be counted, take this
        into account.

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        if rntxt_chord.romanNumeralAlone.lower() == "v":
            return True
        elif (self.allow_root_position_viio_chords
              and "vii" in rntxt_chord.romanNumeralAlone.lower()):
            return True
        elif (not self.allow_root_position_viio_chords
              and "vii" in rntxt_chord.figure.lower()
              and self.check_if_rntxt_chord_is_an_inverted_chord(rntxt_chord)):
            return True
        else:
            return False

    def check_if_rntxt_chord_is_an_inverted_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is inverted.

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        inverted_chord_search = re.search(self.inverted_chord_regex, rntxt_chord.figure)
        if inverted_chord_search:
            return True
        else:
            return False

    def check_if_rntxt_chord_is_allowable_start_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is an allowable start
        chord (either I, V, or VII).

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        if self.check_if_rntxt_chord_is_I_chord(rntxt_chord):
            return True
        elif self.check_if_rntxt_chord_is_V_or_VII_chord(rntxt_chord):
            return True
        else:
            return False

    def check_if_rntxt_chord_is_allowable_end_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is an allowable end
        chord (either I, VI, V, or VII).

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        if self.check_if_rntxt_chord_is_I_chord(rntxt_chord):
            return True
        elif self.check_if_rntxt_chord_is_VI_chord(rntxt_chord):
            return True
        elif self.check_if_rntxt_chord_is_V_or_VII_chord(rntxt_chord):
            return True
        else:
            return False

    def check_if_rntxt_chord_is_VI_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is a VI chord.

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        if rntxt_chord.romanNumeralAlone.lower() == "vi":
            return True
        else:
            return False