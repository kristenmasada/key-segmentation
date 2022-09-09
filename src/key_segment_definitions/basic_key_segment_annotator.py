""" Implementation of Clear Key Segment Definition 1 from thesis.
"""

from foreign_note_detector import ForeignNoteDetector
from key_segment import KeySegment

class BasicKeySegmentAnnotator:
    """ Implementation of Clear Key Segment Definition 1 from thesis.
    Checks for the following criteria when detecting key segments:
    1. The key segment begins on a I or V chord.
    2. It contains a V to I progression.
    3. It ends on a I or V chord.
    4. Any non-scale note is a figuration.

    Also serves as the base class for the implementation of the other
    Clear Key Segment Definitions.
    """

    def __init__(self, parsed_mxl, rntxt_analysis, measure_onset_finder,
                 **kwargs):
        """

        Parameters
        ----------
        parsed_mxl : music21.stream.Score
            Parsed Music21 score for an entire song.
        rntxt_analysis : music21.stream.iterator.RecursiveIterator 
            RomanText chords for the entire song.
        measure_onset_finder : MeasureOnsetFinder
            Used to find the index associated with the last measure in the song.
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

    def get_key_segments(self):
        """ Get all key segments from current song that satisfy the criteria for
        Definition 1.
        """
        modulation_key_segments = self.create_key_segments_from_annotated_modulations()
        key_segments_wo_foreign_notes = self.foreign_note_detector.find_foreign_notes_and_split_key_segments_accordingly(modulation_key_segments)
        trimmed_key_segments = self.trim_key_segments_to_start_and_end_on_allowable_chords(key_segments_wo_foreign_notes)
        key_segments_w_V_to_I_progs = self.remove_key_segments_without_V_to_I_progression(trimmed_key_segments)

        if self.min_key_segment_quarter_length:
            key_segments_w_V_to_I_progs = self.remove_key_segments_shorter_than_min_length(key_segments_w_V_to_I_progs)

        return key_segments_w_V_to_I_progs

    def create_key_segments_from_annotated_modulations(self):
        """ Create list of key segments using annotated modulations.
        These key segments will later be broken down into smaller
        key segments to ensure that they meet the 4 criteria of
        Definition 1.
        """
        key_segments = []
        for rntxt_chord_idx, rntxt_chord in enumerate(self.rntxt_analysis):
            key_name = self.get_key_from_rntxt_chord(rntxt_chord)

            if rntxt_chord_idx == 0:
                current_key_segment = KeySegment(first_rntxt_chord=rntxt_chord,
                                                 score_starts_on_measure_zero=self.score_starts_on_measure_zero,
                                                 rntxt_chords_start_idx=rntxt_chord_idx)
            elif key_name != current_key_segment.key_name:
                current_key_segment.set_offset_and_stop_measure_num_w_rntxt_chord(rntxt_chord)
                current_key_segment.set_rntxt_chords(self.rntxt_analysis, rntxt_chord_idx)
                key_segments.append(current_key_segment)

                current_key_segment = KeySegment(first_rntxt_chord=rntxt_chord,
                                                 score_starts_on_measure_zero=self.score_starts_on_measure_zero,
                                                 rntxt_chords_start_idx=rntxt_chord_idx)

        current_key_segment.set_offset_and_stop_measure_num(self.end_of_score_offset, self.last_measure_num)
        current_key_segment.set_rntxt_chords(self.rntxt_analysis, len(self.rntxt_analysis))
        key_segments.append(current_key_segment)

        return key_segments

    def get_key_from_rntxt_chord(self, rntxt_chord):
        """ Get the current annotated key from a RomanText chord.

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        return rntxt_chord.key.tonicPitchNameWithCase

    def trim_key_segments_to_start_and_end_on_allowable_chords(self, key_segments):
        """ Trim the start and end time of each key segment to ensure that each
        segment starts on a I or V chord and ends on a I or V chord.

        Parameters
        ----------
        key_segments : list of KeySegment
        """
        trimmed_key_segments = []
        for key_segment in key_segments:
            trimmed_key_segment = self.trim_key_segment_to_start_on_allowable_chord(key_segment)

            if trimmed_key_segment is None: # if couldn't find an allowable start chord in the key segment, remove it.
                continue
            else:
                trimmed_key_segment = self.trim_key_segment_to_end_on_allowable_chord(trimmed_key_segment)
                trimmed_key_segments.append(trimmed_key_segment)

        return trimmed_key_segments

    def trim_key_segment_to_start_on_allowable_chord(self, key_segment):
        """ Trim the starting time of the key segment to ensure that the
        segment starts on a I or V chord.

        Parameters
        ----------
        key_segment : KeySegment
        """
        new_key_onset, new_start_measure_num, new_rntxt_chord_idx = None, None, None
        for rntxt_chord_idx, rntxt_chord in enumerate(key_segment.rntxt_chords):
            if self.check_if_rntxt_chord_is_allowable_start_chord(rntxt_chord):
                new_key_onset = rntxt_chord.offset 
                new_start_measure_num = rntxt_chord.measureNumber

                if self.score_starts_on_measure_zero:
                    new_start_measure_num += 1

                new_rntxt_chord_idx = rntxt_chord_idx
                break

        if (new_key_onset is None
            and new_start_measure_num is None): # check if no start chord found.
            return None
        else:
            key_segment.adjust_onset_start_measure_num_and_rntxt_chords(new_key_onset,
                                                                        new_start_measure_num,
                                                                        new_rntxt_chord_idx)
            return key_segment 

    def trim_key_segment_to_end_on_allowable_chord(self, key_segment):
        """ Trim the end time of the key segment to ensure that the
        segment starts on a I or V chord.

        Parameters
        ----------
        key_segment : KeySegment
        """
        for rntxt_chord_reverse_idx, rntxt_chord in enumerate(key_segment.rntxt_chords[::-1]):
            if self.check_if_rntxt_chord_is_allowable_end_chord(rntxt_chord):
                if rntxt_chord_reverse_idx != 0:
                    rntxt_chord_one_ahead_stop_idx = len(key_segment.rntxt_chords) - rntxt_chord_reverse_idx
                    rntxt_chord_one_ahead = key_segment.rntxt_chords[rntxt_chord_one_ahead_stop_idx]
                    key_segment.set_offset_and_stop_measure_num_w_rntxt_chord(rntxt_chord_one_ahead)
                    key_segment.adjust_end_of_rntxt_chords(rntxt_chord_one_ahead_stop_idx)
                break

        return key_segment

    def check_if_rntxt_chord_is_allowable_start_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is an allowable start
        chord (either I or V).

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        if self.check_if_rntxt_chord_is_I_chord(rntxt_chord):
            return True
        elif self.check_if_rntxt_chord_is_V_chord(rntxt_chord):
            return True
        else:
            return False

    def check_if_rntxt_chord_is_allowable_end_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is an allowable end
        chord (either I or V).

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral 
        """
        if self.check_if_rntxt_chord_is_I_chord(rntxt_chord):
            return True
        elif self.check_if_rntxt_chord_is_V_chord(rntxt_chord):
            return True
        else:
            return False

    def remove_key_segments_without_V_to_I_progression(self, key_segments):
        """ Remove any key segments that do not contain a V-to-I progression.

        Parameters
        ----------
        key_segments : list of KeySegment
        """
        key_segments_w_V_to_I_progs = []
        for key_segment in key_segments:
            V_chord_seen = False
            for rntxt_chord in key_segment.rntxt_chords:
                if V_chord_seen and self.check_if_rntxt_chord_is_I_chord(rntxt_chord):
                    key_segments_w_V_to_I_progs.append(key_segment)
                    break
                elif self.check_if_rntxt_chord_is_V_chord(rntxt_chord):
                    V_chord_seen = True

        return key_segments_w_V_to_I_progs

    def check_if_rntxt_chord_is_I_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is a I chord.

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        if rntxt_chord.romanNumeralAlone.lower() == "i":
            return True
        else:
            return False

    def check_if_rntxt_chord_is_V_chord(self, rntxt_chord):
        """ Check if the current RomanText chord is a V chord.

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        if rntxt_chord.romanNumeralAlone.lower() == "v":
            return True
        else:
            return False

    def remove_key_segments_shorter_than_min_length(self, key_segments):
        """ Remove any key segments that are shorter than the minimum
        specified length (in quarter note duration).

        Parameters
        ---------- 
        key_segments : list of KeySegment
        """
        min_length_key_segments = []
        for key_segment in key_segments:
            key_segment_quarter_length = key_segment.offset - key_segment.onset

            if key_segment_quarter_length >= self.min_key_segment_quarter_length:
                min_length_key_segments.append(key_segment)

        return min_length_key_segments