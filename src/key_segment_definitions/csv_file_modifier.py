"""
"""

import csv

from utils import check_and_make_output_dir, convert_camel_case_to_snake_case

ONSET_IDX = 0
OFFSET_IDX = 1
KEY_IDX = 2

class CSVFileModifier:
    """
    """

    def __init__(self, key_segment_annotator_class):
        """
        """
        self.key_segment_annotator_class = convert_camel_case_to_snake_case(key_segment_annotator_class)

    def modify_csv_chords_to_align_w_key_segments(self, key_segments, mxl_filepath):
        """

        Parameters
        ----------
        key_segments : list of KeySegment
        mxl_filepath : str
        """
        csv_filepath = self.convert_mxl_filepath_to_csv_filepath(mxl_filepath)
        chords = self.load_chords_from_csv_file(csv_filepath)
        modified_chords = self.modify_chords(chords, key_segments)

        assert len(modified_chords) == len(chords)

        out_csv_filepath = self.get_out_csv_filepath(csv_filepath)
        self.write_chords_to_csv_file(modified_chords, out_csv_filepath)

    def convert_mxl_filepath_to_csv_filepath(self, mxl_filepath):
        """
        """
        csv_filepath = mxl_filepath.replace('scores', 'chords')
        csv_filepath = csv_filepath.replace('mxl', 'csv')

        return csv_filepath

    def load_chords_from_csv_file(self, in_csv_filepath):
        """

        Parameters
        ----------
        in_csv_filepath : str

        Notes
        -----
        Function modified from frog/preprocessing/preprocess_chords.py.
        """
        with open(in_csv_filepath, mode="r") as f:
            data = csv.reader(f)
            # The data columns are these: start, end, key, degree, quality, inversion
            chords = [ list(row) for row in data ]
        return chords

    def modify_chords(self, chords, key_segments):
        """

        Parameters
        ----------
        chords :
        key_segments :
        """
        modified_chords = []
        for chord in chords:
            chord_onset = float(chord[ONSET_IDX])
            chord_offset = float(chord[OFFSET_IDX])

            chord_found = False
            for key_segment in key_segments:
                if chord_onset >= key_segment.offset:
                    continue
                elif (chord_onset >= key_segment.onset
                      and chord_offset <= key_segment.offset):
                    chord.append("clear")
                    modified_chords.append(chord)
                    chord_found = True
                    break
                elif chord_offset <= key_segment.onset:
                    chord.append("ambiguous")
                    modified_chords.append(chord)
                    chord_found = True
                    break

            if not chord_found:
                chord.append("ambiguous")
                modified_chords.append(chord)

        return modified_chords

    def get_out_csv_filepath(self, csv_filepath):
        """
        """
        out_csv_filepath = csv_filepath.replace('chords', self.key_segment_annotator_class + '_chords')
        return out_csv_filepath

    def write_chords_to_csv_file(self, modified_chords, out_csv_filepath):
        """
        """
        check_and_make_output_dir(out_csv_filepath)

        with open(out_csv_filepath, "w") as fp:
            csv.writer(fp).writerows(modified_chords)