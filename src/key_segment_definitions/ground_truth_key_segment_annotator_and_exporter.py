""" Extract clear key segments from specified songs in Micchi, et al.'s
Meta-Corpus using the ground truth key and chord annotations from the
Meta-Corpus.
"""

from argparse import ArgumentParser

from augmented_6th_key_segment_annotator import Augmented6thKeySegmentAnnotator
from basic_key_segment_annotator import BasicKeySegmentAnnotator
from chromatic_key_segment_annotator import ChromaticKeySegmentAnnotator
from csv_file_modifier import CSVFileModifier
from excluded_events_writer import ExcludedEventsWriter
from key_segment_exporter import KeySegmentExporter 
from key_segment_indices_writer import KeySegmentIndicesWriter 
from measure_onset_finder import MeasureOnsetFinder
from mixture_key_segment_annotator import MixtureKeySegmentAnnotator
from neapolitan_chords_key_segment_annotator import NeapolitanChordsKeySegmentAnnotator
from relaxed_key_segment_annotator import RelaxedKeySegmentAnnotator
from strict_key_segment_annotator import StrictKeySegmentAnnotator
from tonicization_key_segment_annotator import TonicizationKeySegmentAnnotator
from utils import load_filepaths_from_txt_file, load_mxl_file_w_m21, load_rntxt_file_w_m21

class GroundTruthKeySegmentAnnotatorAndExporter:
    """ Extract clear key segments from specified songs in Micchi, et al.'s
    Meta-Corpus using the ground truth key and chord annotations from the
    Meta-Corpus.
    """

    def __init__(self, txt_file_with_mxl_filepaths, key_segment_annotator_class,
                 min_key_segment_quarter_length, output_method,
                 ground_truth_key_labels_npz_path=None, allow_root_position_viio_chords=False):
        """

        Parameters
        ----------
        txt_file_with_mxl_filepaths : str
        key_segment_annotator_class : str
        min_key_segment_quarter_length : int
        output_method : str
        ground_truth_key_labels_npz_path : str
        allow_root_position_viio_chords : bool
        """
        self.mxl_filepaths = load_filepaths_from_txt_file(txt_file_with_mxl_filepaths)
        self.rntxt_filepaths = self.convert_mxl_filepaths_to_rntxt_filepaths(self.mxl_filepaths)

        self.key_segment_annotator_class = key_segment_annotator_class
        self.allow_root_position_viio_chords = allow_root_position_viio_chords

        self.min_key_segment_quarter_length = min_key_segment_quarter_length

        self.output_method = output_method

        if self.output_method == "output_events_to_exclude":
            self.excluded_events_writer = ExcludedEventsWriter(key_segment_annotator_class,
                                                               ground_truth_key_labels_npz_path,
                                                               allow_root_position_viio_chords=allow_root_position_viio_chords)
        elif self.output_method == "output_key_segment_indices":
            self.key_segment_indices_writer = KeySegmentIndicesWriter(key_segment_annotator_class,
                                                                      allow_root_position_viio_chords=allow_root_position_viio_chords)

    def convert_mxl_filepaths_to_rntxt_filepaths(self, mxl_filepaths):
        """ Get RomanText (i.e. rntxt) filepaths from MusicXML (mxl)
        filepaths.

        Parameters
        ----------
        mxl_filepaths : list of str
        """
        rntxt_filepaths = []
        for mxl_filepath in mxl_filepaths:
            rntxt_filepath = mxl_filepath.replace('scores', 'txt')
            rntxt_filepath = rntxt_filepath.replace('mxl', 'txt')
            rntxt_filepaths.append(rntxt_filepath)

        return rntxt_filepaths

    def annotate_and_export_key_segments_for_all_songs(self):
        """ Extract and export key segments for all specified songs.
        """
        for mxl_filepath, rntxt_filepath in zip(self.mxl_filepaths, self.rntxt_filepaths):
            #print("mxl file:", mxl_filepath.split('/')[-1], "rntxt file:", rntxt_filepath.split('/')[-1])

            parsed_mxl = load_mxl_file_w_m21(mxl_filepath)
            rntxt_analysis = load_rntxt_file_w_m21(rntxt_filepath)

            self.annotate_and_export_key_segments_for_song(mxl_filepath, parsed_mxl, rntxt_analysis)

        if self.output_method == "output_events_to_exclude":
            self.excluded_events_writer.write_songs_to_excluded_events_dict_to_npz_file()
        elif self.output_method == "output_key_segment_indices":
            self.key_segment_indices_writer.write_songs_to_key_segment_indices_dict_to_npz_file()

    def annotate_and_export_key_segments_for_song(self, mxl_filepath, parsed_mxl, rntxt_analysis):
        """ Extract and export key segments for a single song.

        Parameters
        ----------
        mxl_filepath : str 
        parsed_mxl : music21.stream.Score
        rntxt_analysis : music21.stream.iterator.RecursiveIterator 
        """
        measure_onset_finder = MeasureOnsetFinder(parsed_mxl)

        song_key_segment_annotator = eval(self.key_segment_annotator_class)(parsed_mxl,
                                                                            rntxt_analysis,
                                                                            measure_onset_finder,
                                                                            min_key_segment_quarter_length=self.min_key_segment_quarter_length,
                                                                            allow_root_position_viio_chords=self.allow_root_position_viio_chords)
        key_segments = song_key_segment_annotator.get_key_segments()

        if self.output_method == "export_key_segments":
            song_key_segment_exporter = KeySegmentExporter(parsed_mxl, measure_onset_finder, mxl_filepath)
            song_key_segment_exporter.extract_and_export_key_segments_to_mxl_files(key_segments)
        elif self.output_method == "output_events_to_exclude":
            self.excluded_events_writer.get_excluded_events_for_song(key_segments, mxl_filepath)
        elif self.output_method == "output_key_segment_indices":
            self.key_segment_indices_writer.get_key_segment_indices_for_song(key_segments, mxl_filepath)

def get_commandline_args():
    """ Get commandline arguments from user.
    """
    parser = ArgumentParser(description='Extract clear key segments from specified songs in Micchi, et al.\'s '
                                        'Meta-Corpus using the ground truth key and chord annotations from the '
                                        'Meta-Corpus.')
    parser.add_argument('--txt_file_with_mxl_filepaths', type=str,
                        help='Text file containing paths to MusicXML files to '
                             'extract key segments from.')
    parser.add_argument('--key_segment_annotator_class', type=str,
                        choices=['BasicKeySegmentAnnotator',
                                 'RelaxedKeySegmentAnnotator',
                                 'StrictKeySegmentAnnotator',
                                 'MixtureKeySegmentAnnotator',
                                 'Augmented6thKeySegmentAnnotator',
                                 'NeapolitanChordsKeySegmentAnnotator',
                                 'ChromaticKeySegmentAnnotator',
                                 'TonicizationKeySegmentAnnotator'],
                        default='BasicKeySegmentAnnotator',
                        help='Clear Key Segment Definition to use when extracting key '
                             'segments.\n'
                             'Class names mapped to Clear Key Segment Definitions in '
                             'thesis:\n'
                             'Definition 1 = `BasicKeySegmentAnnotator`\n'
                             'Definition 2 = `StrictKeySegmentAnnotator`\n'
                             'Definition 3 = `RelaxedKeySegmentAnnotator`\n'
                             'Definition 4 = `ChromaticKeySegmentAnnotator`\n'
                             'Definition 5 = `MixtureKeySegmentAnnotator`\n'
                             'Definition 6 = `NeapolitanKeySegmentAnnotator`\n'
                             'Definition 7 = `Augmented6thKeySegmentAnnotator`\n'
                             'Definition 8 = `TonicizationKeySegmentAnnotator`')
    parser.add_argument('--allow_root_position_viio_chords', action='store_true',
                        help='Allows VII chords in root position to be '
                             'counted as part of dominant harmony. Only '
                             'relevant when `--key_segment_annotator_class` '
                             'option is set to `RelaxedKeySegmentAnnotator`.')
    parser.add_argument('--min_key_segment_quarter_length', type=int,
                        help='The minimum length an extracted key segment should be in '
                             'quarter note duration. Key segments with a shorter '
                             'duration than `min_key_segment_quarter_length` are '
                             'thrown out.')

    parser.add_argument('--key_segments_output_method', type=str,
                        choices=['export_key_segments',
                                 'output_events_to_exclude',
                                 'output_key_segment_indices'],
                        help='`export_key_segments` - '
                             '`output_events_to_exclude` - '
                             '`output_key_segment_indices` - ')

    parser.add_argument('--ground_truth_key_labels_npz_path', type=str,
                        help='Only relevant when `output_events_to_exclude` '
                             'option is chosen for `--key_segments_output_method`.')

    commandline_args = parser.parse_args()

    return commandline_args

if __name__ == '__main__':
    args = get_commandline_args()
    print(args)

    txt_file_with_mxl_filepaths = args.txt_file_with_mxl_filepaths
    key_segment_annotator_class = args.key_segment_annotator_class
    allow_root_position_viio_chords = args.allow_root_position_viio_chords

    min_key_segment_quarter_length = args.min_key_segment_quarter_length

    output_method = args.key_segments_output_method

    ground_truth_key_labels_npz_path = args.ground_truth_key_labels_npz_path

    key_segment_annotator_and_exporter = GroundTruthKeySegmentAnnotatorAndExporter(txt_file_with_mxl_filepaths,
                                                                                   key_segment_annotator_class,
                                                                                   min_key_segment_quarter_length,
                                                                                   output_method,
                                                                                   ground_truth_key_labels_npz_path,
                                                                                   allow_root_position_viio_chords)
    key_segment_annotator_and_exporter.annotate_and_export_key_segments_for_all_songs()