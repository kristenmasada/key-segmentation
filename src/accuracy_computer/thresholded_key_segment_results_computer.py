""" Used to compute all results on the thresholded key segments.
This includes the results provided in Tables 6.2, 6.4, 6.6,
and 6.8 in the thesis.

Table 6.2 - Thresholded key segments (T-KS) results and statistics
(%): C-KS Coverage, System Boundaries (SB) Accuracy, and Complete
Piece (CP) Recall referenced from Table 6.1; Threshold used to
compute thresholded Frog results; Coverage of thresholded Frog
model using Threshold; SB Accuracy computed with Threshold; CP
Recall computed with Threshold with respect to the complete piece.

Table 6.4 - Fragmentation computed for T-KS: Threshold used to
compute thresholded Frog results; Average Segment Length of T-KS;
total number of Segment Events in T-KS; total number of T-KS
Segments. Each event is the length of an eighth note.

Table 6.6 - Results for Whole Thresholded Key Segments (WT-KS):
Whole Segment Accuracy; Whole Segment Event-Level Accuracy.
Extracted segment is correct if the key labels for all events
in the segment are correct.

Table 6.8 - Fragmentation computed for WT-KS: Average Segment
Length of WT-KS; total number of Segment Events in WT-KS; total
number of WT-KS Segments. Each event is the length of an eighth
note.
"""

from argparse import ArgumentParser

import numpy as np

from file_handlers import NpzFileHandler
from fragmentation_computer import FragmentationComputer
from utils import get_consecutive_groups_of_indices, \
                  get_key_segments_from_consecutive_idx_groups, \
                  remove_songs_to_ignore_from_dict, \
                  truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels
from whole_segment_key_accuracy_computer import WholeSegmentKeyAccuracyComputer

class ThresholdedKeySegmentResultsComputer:
    """ Used to compute all results on the thresholded key segments.
    This includes the results provided in Tables 6.2, 6.4, 6.6,
    and 6.8 in the thesis.
    """

    def __init__(self, event_key_probs_dict, ground_truth_key_labels_dict,
                 threshold=0.9):
        """

        Parameters
        ----------
        event_key_probs_dict : dict of { str : np.ndarray (dtype='float32')}
        ground_truth_key_labels_dict : dict of { str : np.ndarray (dtype='int64')}
        threshold : float
        """
        self.songs_to_ignore = ["Mozart_Wolfgang_Amadeus_-___-_K455"]

        self.event_key_probs_dict = remove_songs_to_ignore_from_dict(self.songs_to_ignore, event_key_probs_dict)
        self.ground_truth_key_labels_dict = remove_songs_to_ignore_from_dict(self.songs_to_ignore, ground_truth_key_labels_dict)

        self.event_key_preds_dict = self.get_event_key_preds_dict(self.event_key_probs_dict)

        self.threshold = threshold

        self.truncate_off_by_one_event_key_probs()

    def truncate_off_by_one_event_key_probs(self):
        """ Several songs contain one more event at end in
        event predictions vs. the ground truth labels. For
        now, truncate these.
        """
        for songname in self.event_key_probs_dict:
            self.event_key_probs_dict[songname] = truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels(
                                                                                   self.event_key_probs_dict[songname],
                                                                                   self.ground_truth_key_labels_dict[songname])

    def get_event_key_preds_dict(self, event_key_probs_dict):
        """ Convert the event key probabilities to event key
        predictions. Create a new dictionary to store the
        event key predictions for each song.

        Parameters
        ----------
        event_key_probs_dict : dict of { str : np.ndarray }
        """
        event_key_preds_dict = {}
        for songname in event_key_probs_dict:
            song_event_key_probs = event_key_probs_dict[songname]
            song_key_pred_for_each_event = self.get_key_pred_for_each_event(song_event_key_probs)
            event_key_preds_dict[songname] = song_key_pred_for_each_event

        return event_key_preds_dict

    def compute_max_key_prob_for_each_event(self, song_event_key_probs):
        """ Find the maximum key probability value for each event.

        Parameters
        ----------
        song_event_key_probs : np.ndarray
        """
        return np.max(song_event_key_probs, axis=1)

    def get_key_pred_for_each_event(self, song_event_key_probs):
        """ Find the predicted key label for each event from
        `song_event_key_probs`.

        Parameters
        ----------
        song_event_key_probs : np.ndarray
        """
        return np.argmax(song_event_key_probs, axis=1)

    def get_indices_of_events_w_max_key_prob_greater_than_or_equal_to_threshold(self, song_max_key_prob_for_each_event):
        """ Get the indices of events that have a maximum key
        probability that is >= the threshold.

        Parameters
        ----------
        song_max_key_prob_for_each_event : np.ndarray
        """
        return np.nonzero(song_max_key_prob_for_each_event >= self.threshold)

    def compute_and_output_coverage(self):
        """ Compute and output the complete piece coverage
        for a specific threshold.
        """
        coverage, num_predicted_events, total_num_events = self.compute_coverage()

        print("Coverage (threshold = {:.3f}): {:.1f}% ({}/{})".format(self.threshold,
                                                                      coverage,
                                                                      num_predicted_events,
                                                                      total_num_events))

        return coverage

    def compute_coverage(self):
        """ Compute the overall complete piece coverage.
        """
        num_predicted_events = 0
        total_num_events = 0
        for songname in self.event_key_probs_dict:
            song_event_key_probs = self.event_key_probs_dict[songname]

            song_max_key_prob_for_each_event = self.compute_max_key_prob_for_each_event(song_event_key_probs)
            num_predicted_events += self.compute_num_key_probs_greater_than_or_equal_to_threshold(song_max_key_prob_for_each_event)

            num_song_events = song_max_key_prob_for_each_event.shape[0]
            total_num_events += num_song_events

        coverage = (num_predicted_events / total_num_events) * 100.0
        return coverage, num_predicted_events, total_num_events

    def compute_num_key_probs_greater_than_or_equal_to_threshold(self, song_max_key_prob_for_each_event):
        """ Compute the total number of events that have a maximum key probability
        >= the threshold for one song.

        Parameters
        ----------
        song_max_key_prob_for_each_event : np.ndarray
        """
        return np.sum(song_max_key_prob_for_each_event >= self.threshold)

    def compute_and_output_accuracy_and_recall(self):
        """ Compute and output system-boundaries accuracy
        and complete-piece recall.
        """
        accuracy, recall, num_correctly_predicted_events, num_predicted_events, total_num_events = self.compute_accuracy_and_recall()

        print("Accuracy: {:.1f}% ({}/{})".format(accuracy, num_correctly_predicted_events, num_predicted_events))
        print("Recall: {:.1f}% ({}/{})".format(recall, num_correctly_predicted_events, total_num_events))

        return accuracy

    def compute_accuracy_and_recall(self):
        """ Compute system-boundaries accuracy and
        complete-piece recall.
        """
        num_correctly_predicted_events = 0
        num_predicted_events = 0
        total_num_events = 0

        for songname in self.event_key_probs_dict:
            song_event_key_probs = self.event_key_probs_dict[songname]
            song_key_pred_for_each_event = self.event_key_preds_dict[songname]

            song_ground_truth_key_labels = self.ground_truth_key_labels_dict[songname]

            song_max_key_prob_for_each_event = self.compute_max_key_prob_for_each_event(song_event_key_probs)
            indices_of_events_w_key_prob_gt_or_et_threshold = self.get_indices_of_events_w_max_key_prob_greater_than_or_equal_to_threshold(song_max_key_prob_for_each_event)

            song_key_preds_for_events_w_key_prob_gt_or_et_threshold = song_key_pred_for_each_event[indices_of_events_w_key_prob_gt_or_et_threshold]
            song_ground_truth_key_labels_for_events_w_key_prob_gt_or_et_threshold = song_ground_truth_key_labels[indices_of_events_w_key_prob_gt_or_et_threshold]
            num_correctly_predicted_events += np.sum(song_key_preds_for_events_w_key_prob_gt_or_et_threshold == song_ground_truth_key_labels_for_events_w_key_prob_gt_or_et_threshold)

            num_predicted_events += song_key_preds_for_events_w_key_prob_gt_or_et_threshold.shape[0]
            total_num_events += song_max_key_prob_for_each_event.shape[0]

        accuracy = (num_correctly_predicted_events / num_predicted_events) * 100.0
        recall = (num_correctly_predicted_events / total_num_events) * 100.0
        return accuracy, recall, num_correctly_predicted_events, num_predicted_events, total_num_events

    def update_threshold(self, threshold):
        """ Update the threshold.

        Parameters
        ----------
        threshold : float
        """
        self.threshold = threshold

    def get_key_segments_dict(self):
        """ Get thresholded key segments for each song.
        Place these in a dictionary, where the key is the
        songname and the value is the key segments.
        """
        key_segments_dict = {}

        for songname in self.event_key_probs_dict:
            song_event_key_probs = self.event_key_probs_dict[songname]
            song_max_key_prob_for_each_event = self.compute_max_key_prob_for_each_event(song_event_key_probs)
            indices_of_events_w_key_prob_gt_threshold = self.get_indices_of_events_w_max_key_prob_greater_than_or_equal_to_threshold(
                                                                                                    song_max_key_prob_for_each_event)

            consecutive_idx_groups = get_consecutive_groups_of_indices(indices_of_events_w_key_prob_gt_threshold[0])

            song_key_pred_for_each_event = self.event_key_preds_dict[songname]
            key_segments = get_key_segments_from_consecutive_idx_groups(song_key_pred_for_each_event, consecutive_idx_groups)

            key_segments_dict[songname] = key_segments

        return key_segments_dict

def get_commandline_args():
    """ Get commandline arguments from user.
    """
    parser = ArgumentParser(description='Get thresholded key segments and compute '
                                        'accuracy statistics over these.')
    parser.add_argument('--event_key_probs_npz_path', type=str,
                        help='Path to .npz file containing the event key '
                             'probabilities outputted by the Micchi model.')
    parser.add_argument('--ground_truth_key_labels_npz_path', type=str,
                        help='Path to .npz file containing the ground '
                             'truth key labels for the same songs as '
                             '`--event_key_probs_npz_path`.')
    parser.add_argument('--table', type=str,
                        choices=["6.2", "6.4", "6.6", "6.8"],
                        help="Table 6.2 - Thresholded key segments (T-KS) results and statistics.\n"
                             "Table 6.4 - Fragmentation computed for T-KS.\n"
                             "Table 6.6 - Results for Whole Thresholded Key Segments (WT-KS).\n"
                             "Table 6.8 - Fragmentation computed for WT-KS.")

    commandline_args = parser.parse_args()

    return commandline_args

def compute_accuracy_and_coverage_for_all_thresholds(thresholded_micchi_model,
                                                     thresholds):
    """ Compute complete-piece accuracy and coverage values for
    thresholded key segments using each threshold value.

    Parameters
    ----------
    thresholded_micchi_model : ThresholdedKeySegmentResultsComputer
    thresholds : list of float
    """
    print("Accuracy and Coverage:")
    coverages = []
    accuracies = []
    for threshold in thresholds:
        thresholded_micchi_model.update_threshold(threshold)

        coverage = thresholded_micchi_model.compute_and_output_coverage()
        coverages.append(coverage)

        accuracy = thresholded_micchi_model.compute_and_output_accuracy_and_recall()
        accuracies.append(accuracy)

        print()

def compute_fragmentation_for_all_thresholds(thresholded_micchi_model,
                                             thresholds):
    """ Compute average segment length for thresholded key segments
    using each threshold value.

    Parameters
    ----------
    thresholded_micchi_model : ThresholdedKeySegmentResultsComputer
    thresholds : list of float
    """
    print("\nFragmentation:")
    for threshold in thresholds:
        thresholded_micchi_model.update_threshold(threshold)

        key_segments_dict = thresholded_micchi_model.get_key_segments_dict()

        fragmentation_computer = FragmentationComputer(key_segments_dict,
                                                       threshold)
        fragmentation_computer.compute_and_output_avg_segment_len()

def compute_whole_key_segment_acc_for_all_thresholds(thresholded_micchi_model,
                                                     thresholds):
    """ Compute whole segment accuracy for thresholded key segments
    using each threshold value.

    Parameters
    ----------
    thresholded_micchi_model : ThresholdedKeySegmentResultsComputer
    thresholds : list of float
    """
    for threshold in thresholds:
        thresholded_micchi_model.update_threshold(threshold)
        print("Threshold:", threshold)

        key_segments_dict = thresholded_micchi_model.get_key_segments_dict()

        whole_segment_key_acc_computer = WholeSegmentKeyAccuracyComputer(thresholded_micchi_model.event_key_preds_dict,
                                                                         thresholded_micchi_model.ground_truth_key_labels_dict,
                                                                         key_segments_dict)

        whole_segment_key_acc_computer.compute_whole_segment_key_accuracies_for_all_songs()

def compute_whole_key_segment_fragmentation_for_all_thresholds(thresholded_micchi_model,
                                                               thresholds):
    """ Compute whole segment fragmentation for thresholded key segments
    using each threshold value.

    Parameters
    ----------
    thresholded_micchi_model : ThresholdedKeySegmentResultsComputer
    thresholds : list of float
    """
    for threshold in thresholds:
        thresholded_micchi_model.update_threshold(threshold)
        print("Threshold:", threshold)

        key_segments_dict = thresholded_micchi_model.get_key_segments_dict()

        whole_segment_key_acc_computer = WholeSegmentKeyAccuracyComputer(thresholded_micchi_model.event_key_preds_dict,
                                                                         thresholded_micchi_model.ground_truth_key_labels_dict,
                                                                         key_segments_dict)

        whole_segment_key_acc_computer.compute_whole_segment_key_accuracies_for_all_songs(verbose=False)
        whole_segment_key_acc_computer.compute_fragmentation_for_all_songs()

if __name__ == '__main__':
    args = get_commandline_args()
    print(args)

    npz_file_handler = NpzFileHandler()
    event_key_probs_dict = npz_file_handler.read_npz_file(args.event_key_probs_npz_path)
    ground_truth_key_labels_dict = npz_file_handler.read_npz_file(args.ground_truth_key_labels_npz_path)

    thresholds = [0.98, 0.89, 0.875, 0.87, 0.865, 0.825, 0.81, 0.51, 0.17]
    thresholded_micchi_model = ThresholdedKeySegmentResultsComputer(event_key_probs_dict,
                                                                    ground_truth_key_labels_dict)

    if args.table == "6.2":
        compute_accuracy_and_coverage_for_all_thresholds(thresholded_micchi_model,
                                                         thresholds)
    elif args.table == "6.4":
        compute_fragmentation_for_all_thresholds(thresholded_micchi_model,
                                                 thresholds)
    elif args.table == "6.6":
        compute_whole_key_segment_acc_for_all_thresholds(thresholded_micchi_model,
                                                         thresholds)
    elif args.table == "6.8":
        compute_whole_key_segment_fragmentation_for_all_thresholds(thresholded_micchi_model,
                                                                   thresholds)