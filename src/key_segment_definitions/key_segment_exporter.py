"""
"""

from copy import deepcopy
from os import mkdir
from os.path import basename, dirname, isdir

import music21 as m21

class KeySegmentExporter:
    """
    """

    def __init__(self, parsed_mxl, measure_onset_finder, mxl_filepath=None):
        """

        Parameters
        ----------
        parsed_mxl : music21.stream.Score
        measure_onset_finder : MeasureOnsetFinder
        mxl_filepath : str
        """
        self.parsed_mxl = parsed_mxl

        self.measure_nums_to_measure_onsets = measure_onset_finder.measure_nums_to_measure_onsets
        self.total_num_measures = measure_onset_finder.total_num_measures
        self.parsed_mxl_starts_on_measure_zero = measure_onset_finder.parsed_mxl_starts_on_measure_zero

        if mxl_filepath is not None:
            self.key_segments_output_dir = self.get_key_segments_output_dir_name(mxl_filepath) 
            self.create_key_segments_output_dir_if_dne()

            self.song_name = self.get_songname_from_mxl_path(mxl_filepath)
        else:
            self.key_segments_output_dir = "tmp"
            self.song_name = "tmp"

    def get_key_segments_output_dir_name(self, mxl_filepath):
        """

        Parameters
        ----------
        mxl_filepath : str
        """
        mxl_filepath_dir = dirname(mxl_filepath)
        key_segments_output_dir = mxl_filepath_dir.replace('scores', 'basic_key_segments') # NOTE: will have to change this later.
        return key_segments_output_dir 

    def create_key_segments_output_dir_if_dne(self):
        """
        """
        if not isdir(self.key_segments_output_dir):
            mkdir(self.key_segments_output_dir)

    def get_songname_from_mxl_path(self, mxl_path):
        """

        Parameters
        ----------
        mxl_path: str
        """
        return basename(mxl_path)[:-4]

    def extract_and_export_key_segments_to_mxl_files(self, key_segments):
        """
        """
        for key_segment_idx, key_segment in enumerate(key_segments):
            parsed_mxl_key_segment = self.extract_key_segment_from_parsed_mxl(key_segment)
            self.export_key_segment_to_mxl_file(key_segment_idx, parsed_mxl_key_segment)

    def extract_key_segment_from_parsed_mxl(self, key_segment):
        """

        Parameters
        ----------
        key_segment : KeySegment
        """
        #print("start measure:", key_segment.start_measure_num, "end measure (inclusive):", key_segment.stop_measure_num)
        if self.parsed_mxl_starts_on_measure_zero:
            key_segment_start_measure_num = key_segment.start_measure_num - 1
            key_segment_stop_measure_num = key_segment.stop_measure_num - 1 
        else:
            key_segment_start_measure_num = key_segment.start_measure_num
            key_segment_stop_measure_num = key_segment.stop_measure_num

        key_segment_in_parsed_mxl = deepcopy(self.parsed_mxl.measures(key_segment_start_measure_num, key_segment_stop_measure_num)) # inclusive

        first_measure_onset = self.measure_nums_to_measure_onsets[key_segment.start_measure_num]

        if (key_segment.stop_measure_num+1) > self.total_num_measures:
            first_measure_after_key_segment_offset = self.parsed_mxl.duration.quarterLength
        else:
            try:
                first_measure_after_key_segment_offset = self.measure_nums_to_measure_onsets[key_segment.stop_measure_num+1]
            except:
                breakpoint()

        # remove all notes/chords that come before `key_onset`
        if key_segment.onset > first_measure_onset:
            self.remove_notes_in_first_measure_before_key_segment_onset(key_segment_in_parsed_mxl,
                                                                        first_measure_onset,
                                                                        key_segment.onset)

        # remove all notes/chords that come after `key_offset`
        if key_segment.offset < first_measure_after_key_segment_offset:
            self.remove_notes_in_last_measure_before_key_segment_onset(key_segment_in_parsed_mxl,
                                                                       first_measure_onset,
                                                                       key_segment.offset)

        return key_segment_in_parsed_mxl

    def remove_notes_in_first_measure_before_key_segment_onset(self, key_segment_in_parsed_mxl,
                                                               first_measure_onset, key_segment_onset):
        """
        Notes
        -----
        Not the most efficient implementation. 
        NOTE: really only need to look at the first measure.
        """
        #print("key_segment.onset:", key_segment_onset, "first_measure_onset:", first_measure_onset)
        for stream_element in key_segment_in_parsed_mxl.recurse():
            if (isinstance(stream_element, m21.chord.Chord)
                or isinstance(stream_element, m21.note.Note)):
                stream_element_onset = stream_element.getOffsetInHierarchy(key_segment_in_parsed_mxl)
                adjusted_stream_element_onset = first_measure_onset + stream_element_onset
                if adjusted_stream_element_onset < key_segment_onset:
                    stream_element_idx = stream_element.activeSite.index(stream_element)
                    stream_element.activeSite.pop(stream_element_idx)

    def remove_notes_in_last_measure_before_key_segment_onset(self, key_segment_in_parsed_mxl,
                                                              first_measure_onset, key_segment_offset):
        """
        """
        for stream_element in key_segment_in_parsed_mxl.recurse():
            if (isinstance(stream_element, m21.chord.Chord)
                or isinstance(stream_element, m21.note.Note)):
                stream_element_onset = stream_element.getOffsetInHierarchy(key_segment_in_parsed_mxl)
                adjusted_stream_element_onset = first_measure_onset + stream_element_onset
                if adjusted_stream_element_onset >= key_segment_offset:
                    stream_element_idx = stream_element.activeSite.index(stream_element)
                    stream_element.activeSite.pop(stream_element_idx)

    def export_key_segment_to_mxl_file(self, key_segment_idx, parsed_mxl_key_segment):
        """

        Parameters
        ----------
        key_segment_idx : int
        parsed_mxl_key_segment : 
        """
        key_segment_path = self.get_key_segment_path(key_segment_idx)
        parsed_mxl_key_segment.write('musicxml', fp=key_segment_path)

    def get_key_segment_path(self, key_segment_idx):
        """
        """
        return self.key_segments_output_dir + '/' + self.song_name + '_' + str(key_segment_idx) + '.mxl'