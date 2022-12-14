""" Contains the class to represent a clear key segment object.
"""

ROUNDING_VALUE = 5  # used to round the onset and offset times of a key segment

class KeySegment:
    """ Class to represent a clear key segment object.
    """

    def __init__(self, key_name=None, onset=-1.0, offset=-1.0, start_measure_num=-1,
                 stop_measure_num=-1, rntxt_chords_start_idx=-1, rntxt_chords=[],
                 score_starts_on_measure_zero=False, first_rntxt_chord=None):
        """

        Parameters
        ----------
        key_name : str
            "The pitch name as a string with the proper case (upper = major; lower = minor)"
            (from `Key.tonicPitchNameWithCase` Music21 documentation).
        onset : float
            Onset in quarter length of key segment relative to the start of the score.
        offset : float
            Offset in quarter length of key segment relative to the start of the score.
            Exclusive.
        start_measure_num : int
            The index of the start measure of the key segment.
        stop_measure_num : int
            The index of the stop measure of the key segment. Inclusive.
        rntxt_chords_start_idx : int
            Index of the first RomanText chord in the key segment. Index relative to
            the `rntxt_chords` list.
        rntxt_chords : list of music21.roman.RomanNumeral
            List of RomanText chords that comprise the key segment. May 
            be an empty list until `KeySegment.set_rntxt_chords()` is called.
        score_starts_on_measure_zero : bool
            True if first measure in Music21 has index 0 instead of index 1. If true,
            `start_measure_num` and `stop_measure_num` are shifted one to the right.
        first_rntxt_chord : music21.roman.RomanNumeral
            First RomanText chord in the key segment. Used to get the `key_name`,
            `onset`, and `start_measure_num` of the key segment.
        """
        self.key_name = key_name

        self.onset = onset 
        self.offset = offset 

        self.start_measure_num = start_measure_num
        self.stop_measure_num = stop_measure_num 

        self.rntxt_chords_start_idx = rntxt_chords_start_idx
        self.rntxt_chords = rntxt_chords 

        self.score_starts_on_measure_zero = score_starts_on_measure_zero
        
        if first_rntxt_chord:
            self.initialize_key_segment_using_first_rntxt_chord(first_rntxt_chord)

        if self.score_starts_on_measure_zero:
            self.adjust_start_and_stop_measure_nums_if_score_starts_on_measure_zero()

    def initialize_key_segment_using_first_rntxt_chord(self, first_rntxt_chord):
        """ Initialize the key name, the key segment onset time, and the
        start measure number of a KeySegment object using the first
        RomanText chord that occurs in the key segment.

        Parameters
        ----------
        first_rntxt_chord : music21.roman.RomanNumeral
        """
        self.key_name = first_rntxt_chord.key.tonicPitchNameWithCase
        self.onset = first_rntxt_chord.offset
        self.start_measure_num = first_rntxt_chord.measureNumber

    def adjust_start_and_stop_measure_nums_if_score_starts_on_measure_zero(self):
        """ Shift the start and stop measure numbers by 1, unless their value
        is -1 (meaning the measure numbers are unset).
        """
        if self.start_measure_num != -1:
            self.start_measure_num += 1

        if self.stop_measure_num != -1:
            self.stop_measure_num += 1

    def adjust_onset_start_measure_num_and_rntxt_chords(self, onset, start_measure_num, new_rntxt_chords_start_idx):
        """ Set the onset time and the start measure number for an
        existing KeySegment object. Also update the list of RomanText
        chords contained within the KeySegment object.

        Parameters
        ----------
        onset : float
        start_measure_num : int
        new_rntxt_chords_start_idx : int
        """
        self.onset = onset
        self.start_measure_num = start_measure_num
        self.rntxt_chords = self.rntxt_chords[new_rntxt_chords_start_idx:]

    def set_offset_and_stop_measure_num(self, offset, stop_measure_num):
        """ Set the offset time and the stop measure number for
        an existing KeySegment object.

        Parameters
        ----------
        offset : float
        stop_measure_num : int
        """
        self.offset = offset
        self.stop_measure_num = stop_measure_num

    def set_offset_and_stop_measure_num_w_rntxt_chord(self, rntxt_chord_after_stop_chord):
        """ Set the offset time and the stop measure number for
        an existing KeySegment object using the RomanText chord that
        occurs immediately after the object in the song. 

        Parameters
        ----------
        rntxt_chord_after_stop_chord : music21.roman.RomanNumeral
        """
        self.offset = rntxt_chord_after_stop_chord.offset
        self.stop_measure_num = rntxt_chord_after_stop_chord.measureNumber

        if self.score_starts_on_measure_zero:
            self.stop_measure_num += 1

    def set_rntxt_chords(self, song_rntxt_chords=None, rntxt_chords_stop_idx=None,
                         key_segment_rntxt_chords=None):
        """ Set the list of RomanText chords that the key segment is
        comprised of. Can either be set by passing a list of all of
        the RomanText chords in the song, as well as the RomanText
        chords stop index, or by directly passing the list of RomanText
        chords contained in the key segment.

        Parameters
        ----------
        song_rntxt_chords : list of music21.roman.RomanNumeral
        rntxt_chords_stop_idx : int
            Exclusive.
        key_segment_rntxt_chords : list of music21.roman.RomanNumeral
        """
        if song_rntxt_chords is not None:
            if self.rntxt_chords_start_idx == -1:
                raise Exception("Before calling `set_rntxt_chords()`, `self.rntxt_chords_start_idx` should have a positive value (current value: {}).".format(self.rntxt_chords_start_idx))

            self.rntxt_chords = song_rntxt_chords[self.rntxt_chords_start_idx:rntxt_chords_stop_idx]
        elif key_segment_rntxt_chords is not None:
            self.rntxt_chords = key_segment_rntxt_chords

    def adjust_end_of_rntxt_chords(self, new_rntxt_chords_stop_idx):
        """ Cut off some of the RomanText chords at the end of the key
        segment. Cut off point is specified by `new_rntxt_chords_stop_idx`.

        Parameters
        ----------
        new_rntxt_chords_stop_idx : int
        """
        self.rntxt_chords = self.rntxt_chords[:new_rntxt_chords_stop_idx]

    def __repr__(self):
        """ String representation of KeySegment object.
        """
        return "(key: {}, onset: {}, offset: {}, start measure no.: {}, stop measure no.: {})".format(self.key_name,
                                                                                                      self.onset,
                                                                                                      self.offset,
                                                                                                      self.start_measure_num,
                                                                                                      self.stop_measure_num)

    def __eq__(self, other):
        """ Overload the == operator for the KeySegment class.

        Parameters
        ----------
        other : KeySegment or another type
        """
        if isinstance(other, KeySegment):
            return (self.key_name == other.key_name
                    and round(self.onset, ROUNDING_VALUE) == round(other.onset, ROUNDING_VALUE)
                    and round(self.offset, ROUNDING_VALUE) == round(other.offset, ROUNDING_VALUE)
                    and self.start_measure_num == other.start_measure_num
                    and self.stop_measure_num == other.stop_measure_num)
        return False