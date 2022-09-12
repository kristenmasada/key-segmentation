""" Detects where significant foreign notes occur in the
score by identifying segments labeled with chords that
contain foreign notes. Also used to break up existing
key segments based on where these foreign note chords
occur. Takes into account whether mixture, augmented 6th
chords, and/or Neapolitan chords are allowed. 
"""

import re

from key_segment import KeySegment

class ForeignNoteDetector:
    """ Detects where significant foreign notes occur in the
    score by identifying segments labeled with chords that
    contain foreign notes. Also used to break up existing
    key segments based on where these foreign note chords
    occur. Takes into account whether mixture, augmented 6th
    chords, and/or Neapolitan chords are allowed. 
    """

    def __init__(self, allow_for_mixture=False, allow_aug6_chords=False,
                 allow_neapolitan_chords=False):
        """

        Parameters
        ----------
        allow_for_mixture : bool
        allow_aug6_chords : bool
        allow_neapolitan_chords : bool
        """
        self.allow_for_mixture = allow_for_mixture
        self.allow_aug6_chords = allow_aug6_chords
        self.allow_neapolitan_chords = allow_neapolitan_chords

        self.major_key_diatonic_triads_regex = "(viio|vi|V|IV|iii|ii|I)(64|6/4|63|6/3|6|532|54|5)?9?(\[((add|no)[1-9])+\])*"
        self.major_key_diatonic_seventh_chords_regex = "(viiø|vi|V|IV|iii|ii|I)(732|742|765|7|65|6/5|43|4/3|42|4/2|2)?(M9)?(\[((add|no)[1-9])+\])*"
        self.minor_key_diatonic_triads_regex = "(VII|viio|#vio|VI|V|v|IV|iv|III\+|III|iio|ii|i)(64|6/4|63|6/3|6|532|54|5|4|3|2)?:?9?(\[((add|no)[1-9])+\])*"
        self.minor_key_diatonic_seventh_chords_regex = "(VII|viio|viiø|#viø|VI|V|v|IV|iv|III\+|III|iiø|ii|i)(732|742|765|7|6432|643|654|65|62|6/5|642|64|6|43|4/3|42|4/2|2)?(M9)?(\[((add|no)[1-9])+\])*"

        self.neapolitan_chords_regex = "(n6|N6|(b|-)II(9|7|65|64|6|42)?)"

    def find_foreign_notes_and_split_key_segments_accordingly(self, key_segments):
        """ Detect significant foreign notes* and break up the existing key segments into
        smaller key segments that do not contain these foreign note chords.

        *For the time being, this is equivalent to detecting foreign note chords.

        Parameters
        ----------
        key_segments : list of KeySegment 
        """
        key_segments = self.find_foreign_note_chords_and_split_key_segments_accordingly(key_segments)

        return key_segments

    def find_foreign_note_chords_and_split_key_segments_accordingly(self, key_segments):
        """ Detect foreign note chords and break up the existing key segments into
        smaller key segments that do not contain these foreign note chords.

        Parameters
        ----------
        key_segments : list of KeySegment 
        """
        split_key_segments = []
        for key_segment in key_segments:
            non_foreign_note_chords_key_segment_ranges = self.find_non_foreign_note_chords_key_segment_ranges(key_segment)
            split_key_segments = self.split_key_segment_based_on_non_foreign_note_chord_ranges(key_segment,
                                                                                               split_key_segments,  
                                                                                               non_foreign_note_chords_key_segment_ranges)

        return split_key_segments

    def find_non_foreign_note_chords_key_segment_ranges(self, key_segment):
        """ Detect foreign note chords and break up the key segments
        into smaller key segments based on where these foreign note
        chords occur. 

        Parameters
        ----------
        key_segment : KeySegment

        Returns
        -------
        non_foreign_note_chords_key_segment_ranges : list of (int, int)
            (start_rntxt_chord_idx, end_rntxt_chord_idx). Note that
            `end_rntxt_chord_idx` is exclusive.
            `start_rntxt_chord_idx` indicates the index of the RomanText
            chord each key segment begins with and `end_rntxt_chord_idx`
            is the index of the first RomanText chord that occurs
            immediately after the key segment.

        Notes
        -----
        Example:
        Rntxt chords:
            0.0: <music21.roman.RomanNumeral iv7/iv in e minor>
            1.0: <music21.roman.RomanNumeral iio64 in e minor>
            4.0: <music21.roman.RomanNumeral V7 in e minor>
            8.0: <music21.roman.RomanNumeral i in e minor>
            10.0: <music21.roman.RomanNumeral viio43/v in e minor>
            12.0: <music21.roman.RomanNumeral V6 in e minor>
            14.0: <music21.roman.RomanNumeral iv7/iv in e minor>
            16.0: <music21.roman.RomanNumeral viio43/iv in e minor>
            20.0: <music21.roman.RomanNumeral IV6 in e minor>
            22.0: <music21.roman.RomanNumeral iv6 in e minor>
            25.0: <music21.roman.RomanNumeral iv7/iv in e minor>
            27.0: <music21.roman.RomanNumeral IV6 in e minor>
            28.0: <music21.roman.RomanNumeral iv7/iv in e minor>
        """
        non_foreign_note_chords_key_segment_ranges = []
        key_segment_start_idx = None
        for rntxt_chord_idx, rntxt_chord in enumerate(key_segment.rntxt_chords): 
            if (key_segment_start_idx is not None
                and self.check_if_rntxt_chord_is_foreign_note_chord(rntxt_chord)):
                non_foreign_note_chords_key_segment_ranges.append((key_segment_start_idx, rntxt_chord_idx))

                key_segment_start_idx = None
            elif (key_segment_start_idx is None
                  and not self.check_if_rntxt_chord_is_foreign_note_chord(rntxt_chord)):
                key_segment_start_idx = rntxt_chord_idx

        if key_segment_start_idx is not None:
            non_foreign_note_chords_key_segment_ranges.append((key_segment_start_idx, len(key_segment.rntxt_chords)))

        return non_foreign_note_chords_key_segment_ranges

    def check_if_rntxt_chord_is_foreign_note_chord(self, rntxt_chord):
        """ Check if the current RomanText chord contains a significant
        foreign note. Take into account whether Neapolitan chords,
        augmented 6th chords, and/or mixture are allowed.

        Parameters
        ----------
        rntxt_chord : music21.roman.RomanNumeral
        """
        chord_label = rntxt_chord.figure
        if chord_label.lower() == "cad64":
            return False
        elif (self.allow_neapolitan_chords
              and self.check_if_is_neapolitan_chord(chord_label)):
            return False
        elif self.allow_for_mixture and rntxt_chord.isMixture():
            return False
        elif (self.allow_aug6_chords
              and self.check_if_is_non_tonicized_augmented_6th_chord(chord_label)):
            return False
        elif rntxt_chord.key.mode == 'major':
            return self.check_if_is_non_diatonic_chord_in_major_key(chord_label)
        elif rntxt_chord.key.mode == 'minor':
            return self.check_if_is_non_diatonic_chord_in_minor_key(chord_label)
        else:
            raise Exception("`rntxt_chord.key` has mode other than major or minor ({})".format(rntxt_chord.key.mode))

    def check_if_is_neapolitan_chord(self, chord_label):
        """ Check if the current chord label is a
        Neapolitan chord.

        Parameters
        ----------
        chord_label : str
        """
        neapolitan_chord_search = re.search(self.neapolitan_chords_regex, chord_label)
        if (neapolitan_chord_search
            and chord_label == neapolitan_chord_search.group(0)):
            return True
        else:
            return False

    def check_if_is_non_diatonic_chord_in_major_key(self, chord_label):
        """ Check if the current chord label is considered to be a
        non-diatonic chord in major.

        Parameters
        ----------
        chord_label : str
        """
        major_key_diatonic_triad_search = re.search(self.major_key_diatonic_triads_regex, chord_label)
        major_key_diatonic_seventh_chord_search = re.search(self.major_key_diatonic_seventh_chords_regex, chord_label)
        if (major_key_diatonic_triad_search
            and chord_label == major_key_diatonic_triad_search.group(0)):
            return False
        elif (major_key_diatonic_seventh_chord_search
              and chord_label == major_key_diatonic_seventh_chord_search.group(0)):
            return False
        else:
            return True 

    def check_if_is_non_tonicized_augmented_6th_chord(self, chord_label):
        """ Check if the current chord label is a non-tonicized
        augmented 6th chord.

        Parameters
        ----------
        chord_label : str
        """
        lowercase_chord_label = chord_label.lower()

        if self.check_if_is_tonicization_chord(chord_label):
            return False
        elif ("ger" in lowercase_chord_label
              or "fr" in lowercase_chord_label
              or "it" in lowercase_chord_label):
            return True
        else:
            return False

    def check_if_is_tonicization_chord(self, chord_label):
        """ Check if the chord label indicates a tonicization
        (i.e. check if it contains a '/' followed by another
        Roman Numeral chord symbol to indicate the tonicized
        key).

        Parameters
        ----------
        chord_label : str
        """
        tonicization_chord_search = re.search("/[vi]+", chord_label.lower())
        if tonicization_chord_search:
            return True
        else:
            return False

    def check_if_is_non_diatonic_chord_in_minor_key(self, chord_label):
        """ Check if the current chord label is considered to be a
        non-diatonic chord in minor.

        Parameters
        ----------
        chord_label : str
        """
        minor_key_diatonic_triad_search = re.search(self.minor_key_diatonic_triads_regex, chord_label)
        minor_key_diatonic_seventh_chord_search = re.search(self.minor_key_diatonic_seventh_chords_regex, chord_label)
        if (minor_key_diatonic_triad_search
            and chord_label == minor_key_diatonic_triad_search.group(0)):
            return False
        elif (minor_key_diatonic_seventh_chord_search
              and chord_label == minor_key_diatonic_seventh_chord_search.group(0)):
            return False
        else:
            return True 

    def split_key_segment_based_on_non_foreign_note_chord_ranges(self, key_segment, split_key_segments,  
                                                                 non_foreign_note_chords_key_segment_ranges):
        """ Break up the current key segment into smaller key segments that don't
        contain foreign note chords. If the current key segment contains no
        foreign note chords, it is fine as-is.

        Parameters
        ----------
        key_segment : KeySegment
            Key segment to split.
        split_key_segments : list of KeySegment
            Working list of the new key segments that don't contain foreign note chords.
        non_foreign_note_chords_key_segment_ranges : list of (int, int)
            (start_rntxt_chord_idx, end_rntxt_chord_idx). Note that
            `end_rntxt_chord_idx` is exclusive.
        """
        for (start_idx, end_idx) in non_foreign_note_chords_key_segment_ranges:
            split_key_segment = KeySegment(first_rntxt_chord=key_segment.rntxt_chords[start_idx],
                                           score_starts_on_measure_zero=key_segment.score_starts_on_measure_zero)

            if end_idx == len(key_segment.rntxt_chords):
                split_key_segment.set_offset_and_stop_measure_num(key_segment.offset,
                                                                  key_segment.stop_measure_num)
            else:
                split_key_segment.set_offset_and_stop_measure_num_w_rntxt_chord(key_segment.rntxt_chords[end_idx])

            split_key_segment.set_rntxt_chords(key_segment_rntxt_chords=key_segment.rntxt_chords[start_idx:end_idx])
            split_key_segments.append(split_key_segment)

        return split_key_segments