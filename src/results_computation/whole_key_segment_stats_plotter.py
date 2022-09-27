""" Create the relevant plots for the clear key segments, thresholded key
segments, and clear thresholded key segments depending on which
statistics the user wants to plot (e.g. whole segment precision,
whole segment event-level, recall, etc.).
"""

from argparse import ArgumentParser

from file_handlers import NpzFileHandler
from thresholded_key_segment_results_computer import ThresholdedKeySegmentResultsComputer
from utils import convert_event_key_probs_to_event_key_labels, \
                  remove_songs_to_ignore_from_dict
from whole_segment_key_accuracy_computer import WholeSegmentKeyAccuracyComputer
from whole_key_segment_len_count_plotter import WholeKeySegmentLenCountPlotter
from whole_key_segment_precision_plotter import WholeKeySegmentPrecisionPlotter
from whole_key_segment_recall_plotter import WholeKeySegmentRecallPlotter
from whole_key_segment_event_level_recall_plotter import WholeKeySegmentEventLevelRecallPlotter
from whole_key_segment_stats_computer import WholeKeySegmentStatsComputer

def plot_c_ks_t_ks_and_ct_ks_whole_segment_key_stats(clear_key_definition, song_event_key_probs_dict,
                                                     ground_truth_key_labels_dict,
                                                     predicted_c_ks_key_segment_indices_dict,
                                                     predicted_ct_ks_key_segment_indices_dict, threshold,
                                                     plot_correct_num_segments, plot_correct_num_segments_in_log_space,
                                                     plot_precision, plot_event_level_recall, plot_recall):
    """ Create the relevant plots for the clear key segments, thresholded key
    segments, and clear thresholded key segments depending on which
    statistics the user wants to plot.

    Parameters
    ----------
    clear_key_definition : str
    song_event_key_probs_dict : dict of { str : np.ndarray }
    ground_truth_key_labels_dict : dict of { str : np.ndarray }
    predicted_c_ks_key_segment_indices_dict : dict of { str : np.ndarray }
    predicted_ct_ks_key_segment_indices_dict : dict of { str : np.ndarray }
    threshold : float
    plot_correct_num_segments : bool
    plot_correct_num_segments_in_log_space : bool
    plot_precision : bool
    plot_event_level_recall : bool
    plot_recall : bool
    """
    song_event_key_preds_dict = convert_event_key_probs_to_event_key_labels(song_event_key_probs_dict)
    c_ks_whole_key_segment_stats_computer = get_c_ks_whole_key_segment_stats_computer(song_event_key_preds_dict,
                                                                                      ground_truth_key_labels_dict,
                                                                                      predicted_c_ks_key_segment_indices_dict)

    t_ks_whole_key_segment_stats_computer = get_t_ks_whole_key_segment_stats_computer(song_event_key_probs_dict,
                                                                                      song_event_key_preds_dict,
                                                                                      ground_truth_key_labels_dict,
                                                                                      threshold)

    ct_ks_whole_key_segment_stats_computer = get_ct_ks_whole_key_segment_stats_computer(song_event_key_preds_dict,
                                                                                        ground_truth_key_labels_dict,
                                                                                        predicted_ct_ks_key_segment_indices_dict)

    if plot_correct_num_segments:
        plot_the_correct_num_segments(clear_key_definition, c_ks_whole_key_segment_stats_computer,
                                      t_ks_whole_key_segment_stats_computer, ct_ks_whole_key_segment_stats_computer)

    if plot_correct_num_segments_in_log_space:
        plot_the_correct_num_segments_in_log_space(clear_key_definition, c_ks_whole_key_segment_stats_computer,
                                                   t_ks_whole_key_segment_stats_computer, ct_ks_whole_key_segment_stats_computer)

    if plot_precision:
        plot_the_precision(clear_key_definition, c_ks_whole_key_segment_stats_computer, t_ks_whole_key_segment_stats_computer,
                           ct_ks_whole_key_segment_stats_computer)

    if plot_event_level_recall:
        plot_the_event_level_recall(clear_key_definition, c_ks_whole_key_segment_stats_computer, t_ks_whole_key_segment_stats_computer,
                                    ct_ks_whole_key_segment_stats_computer)

    if plot_recall:
        plot_the_recall(clear_key_definition, c_ks_whole_key_segment_stats_computer, t_ks_whole_key_segment_stats_computer,
                        ct_ks_whole_key_segment_stats_computer)

def get_c_ks_whole_key_segment_stats_computer(song_event_key_preds_dict, ground_truth_key_labels_dict,
                                              predicted_key_segment_indices_dict):
    """ Get the `WholeKeySegmentStatsComputer` object for the
    clear key segments.

    Parameters
    ----------
    song_event_key_preds_dict : dict of { str : np.ndarray } 
    ground_truth_key_labels_dict : dict of { str : np.ndarray }
    predicted_key_segment_indices_dict : dict of { str : np.ndarray }
    """
    c_ks_whole_segment_key_acc_computer = WholeSegmentKeyAccuracyComputer(song_event_key_preds_dict,
                                                                          ground_truth_key_labels_dict,
                                                                          predicted_key_segment_indices_dict)

    return WholeKeySegmentStatsComputer(c_ks_whole_segment_key_acc_computer)

def get_t_ks_whole_key_segment_stats_computer(song_event_key_probs_dict, song_event_key_preds_dict,
                                              ground_truth_key_labels_dict, threshold):
    """ Get the `WholeKeySegmentStatsComputer` object for the
    thresholded key segments.

    Parameters
    ----------
    song_event_key_probs_dict : dict of { str : np.ndarray }
    song_event_key_preds_dict : dict of { str : np.ndarray }
    ground_truth_key_labels_dict : dict of { str : np.ndarray }
    threshold : float 
    """
    thresholded_micchi_model = ThresholdedKeySegmentResultsComputer(song_event_key_probs_dict, ground_truth_key_labels_dict,
                                                      threshold=threshold)
    thresholded_model_key_segments_dict = thresholded_micchi_model.get_key_segments_dict()

    t_ks_whole_segment_key_acc_computer = WholeSegmentKeyAccuracyComputer(song_event_key_preds_dict,
                                                                          ground_truth_key_labels_dict,
                                                                          thresholded_model_key_segments_dict)

    return WholeKeySegmentStatsComputer(t_ks_whole_segment_key_acc_computer) 

def get_ct_ks_whole_key_segment_stats_computer(song_event_key_preds_dict, ground_truth_key_labels_dict,
                                               predicted_key_segment_indices_dict):
    """ Get the `WholeKeySegmentStatsComputer` object for the
    clear thresholded key segments.

    Parameters
    ----------
    song_event_key_preds_dict : dict of { str : np.ndarray } 
    ground_truth_key_labels_dict : dict of { str : np.ndarray }
    predicted_key_segment_indices_dict : dict of { str : np.ndarray }
    """
    ct_ks_whole_segment_key_acc_computer = WholeSegmentKeyAccuracyComputer(song_event_key_preds_dict,
                                                                           ground_truth_key_labels_dict,
                                                                           predicted_key_segment_indices_dict)
    return WholeKeySegmentStatsComputer(ct_ks_whole_segment_key_acc_computer)

def plot_the_correct_num_segments(clear_key_definition, c_ks_whole_key_segment_stats_computer,
                                  t_ks_whole_key_segment_stats_computer, ct_ks_whole_key_segment_stats_computer):
    """ Plot the no. correctly predicted segments for each
    segment length for the clear, thresholded, and clear
    thresholded key segments. 

    Parameters
    ----------
    clear_key_definition : str
    c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer 
    t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    """
    whole_key_segment_stats_plotter = WholeKeySegmentLenCountPlotter(clear_key_definition,
                                                                     c_ks_whole_key_segment_stats_computer,
                                                                     t_ks_whole_key_segment_stats_computer,
                                                                     ct_ks_whole_key_segment_stats_computer,
                                                                     plot_in_log_space=False)

    whole_key_segment_stats_plotter.plot_seg_len_vs_correct_segments()

def plot_the_correct_num_segments_in_log_space(clear_key_definition, c_ks_whole_key_segment_stats_computer,
                                               t_ks_whole_key_segment_stats_computer, ct_ks_whole_key_segment_stats_computer):
    """ Plot the no. correctly predicted segments in log space for
    each segment length for the clear, thresholded, and clear
    thresholded key segments. 

    Parameters
    ----------
    clear_key_definition : str
    c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer 
    t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    """
    whole_key_segment_stats_plotter = WholeKeySegmentLenCountPlotter(clear_key_definition,
                                                                     c_ks_whole_key_segment_stats_computer,
                                                                     t_ks_whole_key_segment_stats_computer,
                                                                     ct_ks_whole_key_segment_stats_computer,
                                                                     plot_in_log_space=True)

    whole_key_segment_stats_plotter.plot_seg_len_vs_correct_segments_in_log_space()

def plot_the_precision(clear_key_definition, c_ks_whole_key_segment_stats_computer,
                       t_ks_whole_key_segment_stats_computer,
                       ct_ks_whole_key_segment_stats_computer):
    """ Plot the cumulative whole segment precision values for each
    segment length for the clear, thresholded, and clear thresholded
    key segments.

    Parameters
    ---------
    clear_key_definition : str
    c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer 
    t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    """
    whole_key_segment_precision_plotter = WholeKeySegmentPrecisionPlotter(clear_key_definition,
                                                                          c_ks_whole_key_segment_stats_computer,
                                                                          t_ks_whole_key_segment_stats_computer,
                                                                          ct_ks_whole_key_segment_stats_computer)
    whole_key_segment_precision_plotter.plot_seg_len_vs_precision()

def plot_the_event_level_recall(clear_key_definition, c_ks_whole_key_segment_stats_computer,
                                t_ks_whole_key_segment_stats_computer, ct_ks_whole_key_segment_stats_computer):
    """ Plot the cumulative whole segment event-level recall values
    for each segment length for the clear, thresholded, and clear
    thresholded key segments.

    Parameters
    ----------
    clear_key_definition : str
    c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer 
    t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    """
    whole_key_segment_event_level_recall_plotter = WholeKeySegmentEventLevelRecallPlotter(clear_key_definition,
                                                                                          c_ks_whole_key_segment_stats_computer,
                                                                                          t_ks_whole_key_segment_stats_computer,
                                                                                          ct_ks_whole_key_segment_stats_computer)
    whole_key_segment_event_level_recall_plotter.plot_seg_len_vs_event_level_recall()

def plot_the_recall(clear_key_definition, c_ks_whole_key_segment_stats_computer, t_ks_whole_key_segment_stats_computer,
                    ct_ks_whole_key_segment_stats_computer):
    """ Plot the cumulative whole segment recall values for each segment length
    for the clear, thresholded, and clear thresholded key segments.

    Parameters
    ----------
    clear_key_definition : str
    c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer 
    t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
    """
    whole_key_segment_recall_plotter = WholeKeySegmentRecallPlotter(clear_key_definition,
                                                                    c_ks_whole_key_segment_stats_computer,
                                                                    t_ks_whole_key_segment_stats_computer,
                                                                    ct_ks_whole_key_segment_stats_computer)
    whole_key_segment_recall_plotter.plot_seg_len_vs_recall()

def get_commandline_args():
    """ Get commandline arguments from user.
    """
    parser = ArgumentParser(description='Create the relevant plots for the clear key segments, thresholded key ' 
                                        'segments, and clear thresholded key segments depending on which '
                                        'statistics the user wants to plot (e.g. whole segment precision, '
                                        'whole segment event-level, recall, etc.)')
    parser.add_argument('--event_key_probs_npz_path', type=str,
                        help='Path to .npz file containing the event key '
                             'probabilities outputted by the Micchi model.')
    parser.add_argument('--ground_truth_key_labels_npz_path', type=str,
                        help='Path to .npz file containing the ground '
                             'truth key labels for the same songs as '
                             '`--event_key_probs_npz_path`.')
    parser.add_argument('--clear_key_definition', type=str,
                        choices=['def1', 'def3v2', 'def4v2'],
                        default='def1',
                        help='Definition 1 = Clear key from tonic and dominant chords.\n'
                             'Definition 3, Version 2 = Tonic and dominant harmonies (allow root position viio).\n'
                             'Definition 4, Version 2 = Tonic and dominant harmonies + all chromaticism\n'
                             '(Neapolitan, aug. 6, and mixture) (allow root position viio).')
    parser.add_argument('--threshold', type=float,
                        help='Threshold to use for thresholded Micchi model.')
    parser.add_argument('--plot_correct_num_segments', action='store_true')
    parser.add_argument('--plot_precision', action='store_true')
    parser.add_argument('--plot_recall', action='store_true')
    parser.add_argument('--plot_event_level_recall', action='store_true')
    parser.add_argument('--plot_correct_num_segments_in_log_space', action='store_true')

    commandline_args = parser.parse_args()

    return commandline_args

if __name__ == '__main__':
    args = get_commandline_args()
    print(args)

    songs_to_ignore = ['Mozart_Wolfgang_Amadeus_-___-_K455']

    npz_file_handler = NpzFileHandler()
    song_event_key_probs_dict = npz_file_handler.read_npz_file(args.event_key_probs_npz_path)
    song_event_key_probs_dict = remove_songs_to_ignore_from_dict(songs_to_ignore, song_event_key_probs_dict)
    ground_truth_key_labels_dict = npz_file_handler.read_npz_file(args.ground_truth_key_labels_npz_path)
    ground_truth_key_labels_dict = remove_songs_to_ignore_from_dict(songs_to_ignore, ground_truth_key_labels_dict)

    clear_key_definition = args.clear_key_definition

    predicted_c_ks_key_segment_indices_npz_path = 'in/key_segment_boundaries/meta-corpus_validation_pred_key_segment_boundaries_' + clear_key_definition + '.npz'
    predicted_c_ks_key_segment_indices_dict = npz_file_handler.read_npz_file(predicted_c_ks_key_segment_indices_npz_path)
    predicted_c_ks_key_segment_indices_dict = remove_songs_to_ignore_from_dict(songs_to_ignore, predicted_c_ks_key_segment_indices_dict)

    predicted_ct_ks_key_segment_indices_npz_path = 'in/thresholded_key_segment_boundaries/meta-corpus_validation_thresholded_pred_key_segment_boundaries_' + clear_key_definition + '.npz' 
    predicted_ct_ks_key_segment_indices_dict = npz_file_handler.read_npz_file(predicted_ct_ks_key_segment_indices_npz_path)
    predicted_ct_ks_key_segment_indices_dict = remove_songs_to_ignore_from_dict(songs_to_ignore, predicted_ct_ks_key_segment_indices_dict)

    threshold = args.threshold

    plot_correct_num_segments = args.plot_correct_num_segments
    plot_precision = args.plot_precision
    plot_recall = args.plot_recall
    plot_event_level_recall = args.plot_event_level_recall
    plot_correct_num_segments_in_log_space = args.plot_correct_num_segments_in_log_space

    plot_c_ks_t_ks_and_ct_ks_whole_segment_key_stats(clear_key_definition,
                                                     song_event_key_probs_dict,
                                                     ground_truth_key_labels_dict,
                                                     predicted_c_ks_key_segment_indices_dict,
                                                     predicted_ct_ks_key_segment_indices_dict,
                                                     threshold,
                                                     plot_correct_num_segments,
                                                     plot_correct_num_segments_in_log_space,
                                                     plot_precision,
                                                     plot_event_level_recall,
                                                     plot_recall)