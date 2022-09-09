"""
"""

import music21

from key_segment import KeySegment
from key_segment_exporter import KeySegmentExporter 
from thresholded_basic_key_segment_annotator import ThresholdedBasicKeySegmentAnnotator

NUM_TRIAD_NOTES = 3

class ThresholdedStrictKeySegmentAnnotator(ThresholdedBasicKeySegmentAnnotator):
    """
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
            The index associated with the last measure in the song.
        thresholded_key_segment_indices : list of [int, int]
        min_key_segment_quarter_length : int
            The minimum length a key segment should be in quarter note duration.
        """
        self.song_key_segment_exporter = KeySegmentExporter(parsed_mxl, measure_onset_finder)
        super().__init__(parsed_mxl, rntxt_analysis, measure_onset_finder,
                         thresholded_key_segment_indices, **kwargs)

    def trim_key_segment_to_start_on_allowable_chord(self, key_segment):
        """
        """
        new_key_onset, new_start_measure_num, new_rntxt_chord_idx = None, None, None
        for rntxt_chord_idx, rntxt_chord in enumerate(key_segment.rntxt_chords):
            if self.check_if_rntxt_chord_is_allowable_start_chord(rntxt_chord_idx, key_segment.rntxt_chords, key_segment):
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

    def check_if_rntxt_chord_is_allowable_start_chord(self, rntxt_chord_idx, rntxt_chords, key_segment):
        """
        """
        return self.check_if_rntxt_chord_is_allowable_start_or_end_chord(rntxt_chord_idx, rntxt_chords,
                                                                         key_segment)

    def check_if_rntxt_chord_is_allowable_start_or_end_chord(self, rntxt_chord_idx, rntxt_chords,
                                                             key_segment):
        """ Check if complete I or V triad.
        """
        current_rntxt_chord = rntxt_chords[rntxt_chord_idx]

        if (self.check_if_rntxt_chord_is_I_chord(current_rntxt_chord)
            or self.check_if_rntxt_chord_is_V_chord(current_rntxt_chord)):
            chord_triad_pitches = self.get_triad_pitches_in_rntxt_chord(current_rntxt_chord)
            if len(chord_triad_pitches) < NUM_TRIAD_NOTES:
                return False

            key_segment = self.get_key_segment_from_single_rntxt_chord(rntxt_chord_idx, rntxt_chords, key_segment)
            parsed_mxl_key_segment = self.song_key_segment_exporter.extract_key_segment_from_parsed_mxl(key_segment)
            return self.check_if_rntxt_chord_is_complete_triad(parsed_mxl_key_segment, chord_triad_pitches)
        else:
            return False

    def get_key_segment_from_single_rntxt_chord(self, rntxt_chord_idx, rntxt_chords, key_segment):
        """
        """
        current_rntxt_chord = rntxt_chords[rntxt_chord_idx]
        current_key_segment = KeySegment(first_rntxt_chord=current_rntxt_chord,
                                         score_starts_on_measure_zero=self.score_starts_on_measure_zero,
                                         rntxt_chords_start_idx=rntxt_chord_idx)
        next_rntxt_chord_idx = rntxt_chord_idx + 1
        if next_rntxt_chord_idx == len(rntxt_chords):
            current_key_segment.set_offset_and_stop_measure_num(key_segment.offset, key_segment.stop_measure_num)
        else:
            next_rntxt_chord = rntxt_chords[next_rntxt_chord_idx]
            current_key_segment.set_offset_and_stop_measure_num_w_rntxt_chord(next_rntxt_chord)

        return current_key_segment

    def get_triad_pitches_in_rntxt_chord(self, rntxt_chord):
        """
        """
        rntxt_triad_pitches = []

        if rntxt_chord.root() is not None:
            rntxt_triad_pitches.append(rntxt_chord.root().name)

        if rntxt_chord.third is not None:
            rntxt_triad_pitches.append(rntxt_chord.third.name)

        if rntxt_chord.fifth is not None:
            rntxt_triad_pitches.append(rntxt_chord.fifth.name)

        return rntxt_triad_pitches

    def check_if_rntxt_chord_is_complete_triad(self, parsed_mxl_key_segment, chord_triad_pitches):
        """

        Parameters
        ----------
        parsed_mxl_key_segment : music21.stream.Score
        chord_pitches : list of str

        Notes
        -----
        What does Micchi do about notes that have a duration less than a 32nd?
        """
        key_segment_notes = parsed_mxl_key_segment.flat.getElementsByClass([music21.note.Note, music21.chord.Chord])
        key_segment_pitches = set()
        for note in key_segment_notes:
            if isinstance(note, music21.note.Note):
                key_segment_pitches.add(note.pitch.name)
            elif isinstance(note, music21.chord.Chord):
                for pitch in note.pitches:
                    key_segment_pitches.add(pitch.name)

        full_triad_coverage = True
        for pitch in chord_triad_pitches:
            if pitch not in key_segment_pitches:
                full_triad_coverage = False
                break

        return full_triad_coverage

    def trim_key_segment_to_end_on_allowable_chord(self, key_segment):
        """
        """
        for rntxt_chord_reverse_idx, rntxt_chord in enumerate(key_segment.rntxt_chords[::-1]):
            rntxt_chord_idx = len(key_segment.rntxt_chords) - rntxt_chord_reverse_idx - 1
            if self.check_if_rntxt_chord_is_allowable_end_chord(rntxt_chord_idx, key_segment.rntxt_chords, key_segment):
                if rntxt_chord_reverse_idx != 0:
                    rntxt_chord_one_ahead_stop_idx = rntxt_chord_idx + 1
                    rntxt_chord_one_ahead = key_segment.rntxt_chords[rntxt_chord_one_ahead_stop_idx]
                    key_segment.set_offset_and_stop_measure_num_w_rntxt_chord(rntxt_chord_one_ahead)
                    key_segment.adjust_end_of_rntxt_chords(rntxt_chord_one_ahead_stop_idx)
                break

        return key_segment

    def check_if_rntxt_chord_is_allowable_end_chord(self, rntxt_chord_idx, rntxt_chords, key_segment):
        """ Check if complete I or V triad.
        """
        return self.check_if_rntxt_chord_is_allowable_start_or_end_chord(rntxt_chord_idx, rntxt_chords, key_segment)