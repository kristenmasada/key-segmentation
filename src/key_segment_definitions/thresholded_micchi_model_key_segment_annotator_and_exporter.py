""" Extract thresholded clear key segments from specified songs in
Micchi, et al.'s Meta-Corpus using the key and chord predictions
from the Frog model.
"""

from argparse import ArgumentParser

from file_handlers import NpzFileHandler
from key_segment import KeySegment
from key_segment_indices_writer import KeySegmentIndicesWriter 
from measure_onset_finder import MeasureOnsetFinder
from thresholded_basic_key_segment_annotator import ThresholdedBasicKeySegmentAnnotator
from thresholded_chromatic_key_segment_annotator import ThresholdedChromaticKeySegmentAnnotator
from thresholded_relaxed_key_segment_annotator import ThresholdedRelaxedKeySegmentAnnotator
from thresholded_strict_key_segment_annotator import ThresholdedStrictKeySegmentAnnotator
from thresholded_micchi_model import ThresholdedMicchiModel
from utils import load_filepaths_from_txt_file, load_mxl_file_w_m21, \
                  load_rntxt_file_w_m21, strip_songname_from_path

class ThresholdedMicchiModelKeySegmentAnnotatorAndExporter:
    """ Extract thresholded clear key segments from specified songs in
    Micchi, et al.'s Meta-Corpus using the key and chord predictions
    from the Frog model.
    """

    def __init__(self, event_key_probs_dict, ground_truth_key_labels_dict,
                 threshold, txt_file_with_mxl_filepaths, predicted_rntxt_filepaths_dir,
                 key_segment_annotator_class, min_key_segment_quarter_length):
        """

        Parameters
        ----------
        event_key_probs_dict : dict of { str : np.ndarray } 
        ground_truth_key_labels_dict : dict of { str : np.ndarray }
        threshold : float
        txt_file_with_mxl_filepaths : str
        predicted_rntxt_filepaths_dir : str
        key_segment_annotator_class : str
        min_key_segment_quarter_length : float
        """
        self.songs_to_ignore = ["Mozart_Wolfgang_Amadeus_-___-_K455"]

        self.mxl_filepaths = load_filepaths_from_txt_file(txt_file_with_mxl_filepaths)
        self.mxl_filepaths = self.remove_ignored_songs(self.mxl_filepaths)
        self.rntxt_filepaths = self.convert_mxl_filepaths_to_rntxt_filepaths(self.mxl_filepaths,
                                                                             predicted_rntxt_filepaths_dir)

        self.thresholded_key_segment_indices_dict = self.get_thresholded_key_segment_indices_dict(event_key_probs_dict,
                                                                                                  ground_truth_key_labels_dict,
                                                                                                  threshold)

        self.key_segment_annotator_class = key_segment_annotator_class
        self.min_key_segment_quarter_length = min_key_segment_quarter_length

        self.key_segment_indices_writer = KeySegmentIndicesWriter(key_segment_annotator_class,
                                                                  micchi_predictions=True,
                                                                  allow_root_position_viio_chords=False,
                                                                  thresholded=True)

    def convert_mxl_filepaths_to_rntxt_filepaths(self, mxl_filepaths, predicted_rntxt_filepaths_dir):
        """ Get path to RomanText file for each song.

        Parameters
        ----------
        mxl_filepaths : list of str
        predicted_rntxt_filepaths_dir : str 
        """
        rntxt_filepaths = []
        for mxl_filepath in mxl_filepaths:
            songname = strip_songname_from_path(mxl_filepath)
            rntxt_filepath = predicted_rntxt_filepaths_dir + songname + '.rntxt'
            rntxt_filepaths.append(rntxt_filepath)

        return rntxt_filepaths

    def remove_ignored_songs(self, mxl_filepaths):
        """ Remove songs that should be ignored from list of MusicXML
        files to extract clear key segments from.

        Parameters
        ----------
        mxl_filepaths : list of str
        """
        mxl_filepaths_to_keep = []

        for mxl_filepath in mxl_filepaths:
            songname = strip_songname_from_path(mxl_filepath)

            if songname not in self.songs_to_ignore:
                mxl_filepaths_to_keep.append(mxl_filepath)

        return mxl_filepaths_to_keep

    def get_thresholded_key_segment_indices_dict(self, event_key_probs_dict, ground_truth_key_labels_dict,
                                                 threshold):
        """ For each song, get the eighth note beat start and stop indices
        of each thresholded key segment.

        Parameters
        ----------
        event_key_probs_dict : dict of { str : np.ndarray } 
        ground_truth_key_labels_dict : dict of { str : np.ndarray }
        threshold : float
        """
        thresholded_micchi_model = ThresholdedMicchiModel(event_key_probs_dict, ground_truth_key_labels_dict,
                                                          threshold=threshold)
        return thresholded_micchi_model.get_key_segment_indices_dict()

    def annotate_and_export_key_segments_for_all_songs(self):
        """ Extract and export key segments for all specified songs.
        """
        for mxl_filepath, rntxt_filepath in zip(self.mxl_filepaths, self.rntxt_filepaths):
            print("mxl file:", mxl_filepath.split('/')[-1], "rntxt file:", rntxt_filepath.split('/')[-1])

            parsed_mxl = load_mxl_file_w_m21(mxl_filepath)
            rntxt_analysis = load_rntxt_file_w_m21(rntxt_filepath)

            songname = strip_songname_from_path(mxl_filepath)

            song_thresholded_key_segment_indices = self.thresholded_key_segment_indices_dict[songname] 

            self.annotate_and_export_key_segments_for_song(mxl_filepath, parsed_mxl, rntxt_analysis,
                                                           song_thresholded_key_segment_indices)

        self.key_segment_indices_writer.write_songs_to_key_segment_indices_dict_to_npz_file()

    def annotate_and_export_key_segments_for_song(self, mxl_filepath, parsed_mxl, rntxt_analysis,
                                                  thresholded_key_segment_indices):
        """ Extract and export predicted key segments for a single song.

        Parameters
        ----------
        mxl_filepath : str 
        parsed_mxl : music21.stream.Score
        rntxt_analysis : music21.stream.iterator.RecursiveIterator 
        thresholded_key_segment_indices : list of [int, int]
        """
        measure_onset_finder = MeasureOnsetFinder(parsed_mxl)

        song_key_segment_annotator = eval(self.key_segment_annotator_class)(parsed_mxl,
                                                                            rntxt_analysis,
                                                                            measure_onset_finder,
                                                                            thresholded_key_segment_indices,
                                                                            min_key_segment_quarter_length=self.min_key_segment_quarter_length)
        key_segments = song_key_segment_annotator.get_key_segments()

        self.key_segment_indices_writer.get_key_segment_indices_for_song(key_segments, mxl_filepath)

def get_commandline_args():
    """ Get commandline arguments from user.
    """
    parser = ArgumentParser(description='Extract thresholded clear key segments '
                                        'from specified songs in Micchi, et al.\'s '
                                        'Meta-Corpus using the key and chord predictions '
                                        'from the Frog model.')
    parser.add_argument('--txt_file_with_mxl_filepaths', type=str,
                        help='Text file containing paths to MusicXML files to '
                             'extract key segments from.')
    parser.add_argument('--predicted_rntxt_filepaths_dir', type=str,
                        help='Path to RomanText files corresponding to songs '
                             'specified in `--txt_file_with_mxl_filepaths`.')
    parser.add_argument('--key_segment_annotator_class', type=str,
                        choices=['ThresholdedStrictKeySegmentAnnotator',
                                 'ThresholdedBasicKeySegmentAnnotator',
                                 'ThresholdedRelaxedKeySegmentAnnotator',
                                 'ThresholdedChromaticKeySegmentAnnotator'],
                        default='ThresholdedBasicKeySegmentAnnotator',
                        help='Thresholded Clear Key Segment Definition to use when '
                             'extracting key segments.\n'
                             'Class names mapped to Clear Key Segment Definitions in '
                             'thesis:\n'
                             'Definition 1 = `ThresholdedBasicKeySegmentAnnotator`\n'
                             'Definition 2 = `ThresholdedStrictKeySegmentAnnotator`\n'
                             'Definition 3 = `ThresholdedRelaxedKeySegmentAnnotator`\n'
                             'Definition 4 = `ThresholdedChromaticKeySegmentAnnotator`\n')
    parser.add_argument('--min_key_segment_quarter_length', type=int,
                        help='The minimum length an extracted key segment should be in '
                             'quarter note duration. Key segments with a shorter '
                             'duration than `min_key_segment_quarter_length` are '
                             'thrown out.')

    parser.add_argument('--event_key_probs_npz_path', type=str,
                        help='Path to .npz file containing the event key '
                             'probabilities outputted by the Micchi model.')
    parser.add_argument('--ground_truth_key_labels_npz_path', type=str,
                        help='Path to .npz file containing the ground '
                             'truth key labels for the same songs as '
                             '`--event_key_probs_npz_path`.')
    parser.add_argument('--threshold', type=float,
                        help='Threshold to use for extracting events.')

    commandline_args = parser.parse_args()

    return commandline_args

if __name__ == '__main__':
    args = get_commandline_args()
    print(args)

    txt_file_with_mxl_filepaths = args.txt_file_with_mxl_filepaths
    predicted_rntxt_filepaths_dir = args.predicted_rntxt_filepaths_dir

    key_segment_annotator_class = args.key_segment_annotator_class
    min_key_segment_quarter_length = args.min_key_segment_quarter_length

    npz_file_handler = NpzFileHandler()
    event_key_probs_dict = npz_file_handler.read_npz_file(args.event_key_probs_npz_path)
    ground_truth_key_labels_dict = npz_file_handler.read_npz_file(args.ground_truth_key_labels_npz_path)

    threshold = args.threshold

    thresholded_micchi_model_key_segment_annotator_and_exporter = ThresholdedMicchiModelKeySegmentAnnotatorAndExporter(event_key_probs_dict,
                                                                                                                       ground_truth_key_labels_dict,
                                                                                                                       threshold,
                                                                                                                       txt_file_with_mxl_filepaths,
                                                                                                                       predicted_rntxt_filepaths_dir, 
                                                                                                                       key_segment_annotator_class,
                                                                                                                       min_key_segment_quarter_length)

    thresholded_micchi_model_key_segment_annotator_and_exporter.annotate_and_export_key_segments_for_all_songs()