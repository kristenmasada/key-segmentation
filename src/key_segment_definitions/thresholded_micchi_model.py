"""
"""

from argparse import ArgumentParser

from matplotlib import pyplot as plt
import numpy as np

from file_handlers import NpzFileHandler
from fragmentation_computer import FragmentationComputer, \
                                   SegmentLengthToFrequencyPlotter
from accuracy_computer_utils import get_consecutive_groups_of_indices, \
                                    get_key_segments_from_consecutive_idx_groups, \
                                    remove_songs_to_ignore_from_dict, \
                                    truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels
from whole_segment_key_accuracy_computer import WholeSegmentKeyAccuracyComputer

class ThresholdedMicchiModel:
    """
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
        """
        """
        for songname in self.event_key_probs_dict:
            self.event_key_probs_dict[songname] = truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels(
                                                                                   self.event_key_probs_dict[songname],
                                                                                   self.ground_truth_key_labels_dict[songname])

    def get_event_key_preds_dict(self, event_key_probs_dict):
        """

        Parameters
        ----------
        event_key_probs_dict : dict of {str: np.ndarray}
        """
        event_key_preds_dict = {}
        for songname in event_key_probs_dict:
            song_event_key_probs = event_key_probs_dict[songname]
            song_key_pred_for_each_event = self.get_key_pred_for_each_event(song_event_key_probs)
            event_key_preds_dict[songname] = song_key_pred_for_each_event

        return event_key_preds_dict

    def compute_max_key_prob_for_each_event(self, song_event_key_probs):
        """

        Parameters
        ----------
        song_event_key_probs : np.ndarray (dtype='') 
        """
        return np.max(song_event_key_probs, axis=1) 

    def get_key_pred_for_each_event(self, song_event_key_probs):
        """

        parameters
        ----------
        song_event_key_probs
        """
        return np.argmax(song_event_key_probs, axis=1)

    def get_indices_of_events_w_max_key_prob_greater_than_or_equal_to_threshold(self, song_max_key_prob_for_each_event):
        """

        parameters
        ----------
        song_event_key_probs : 
        """
        return np.nonzero(song_max_key_prob_for_each_event >= self.threshold)

    def compute_and_output_coverage(self):
        """
        """
        coverage, num_predicted_events, total_num_events = self.compute_coverage()

        print("Coverage (threshold = {:.3f}): {:.2f}% ({}/{})".format(self.threshold,
                                                                      coverage,
                                                                      num_predicted_events,
                                                                      total_num_events))

        return coverage

    def compute_coverage(self):
        """
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
        """
        """
        return np.sum(song_max_key_prob_for_each_event >= self.threshold)

    def compute_and_output_accuracy_and_recall(self):
        """
        """
        accuracy, recall, num_correctly_predicted_events, num_predicted_events, total_num_events = self.compute_accuracy_and_recall()

        print("Accuracy: {:.2f}% ({}/{})".format(accuracy, num_correctly_predicted_events, num_predicted_events))
        print("Recall: {:.2f}% ({}/{})".format(recall, num_correctly_predicted_events, total_num_events))

        return accuracy

    def compute_accuracy_and_recall(self):
        """
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
        """
        """
        self.threshold = threshold

    def get_key_segment_indices_dict(self):
        """
        """
        key_segment_indices_dict = {}

        for songname in self.event_key_probs_dict:
            song_event_key_probs = self.event_key_probs_dict[songname]
            song_max_key_prob_for_each_event = self.compute_max_key_prob_for_each_event(song_event_key_probs)
            indices_of_events_w_key_prob_gt_threshold = self.get_indices_of_events_w_max_key_prob_greater_than_or_equal_to_threshold(
                                                                                                    song_max_key_prob_for_each_event) 

            consecutive_idx_groups = get_consecutive_groups_of_indices(indices_of_events_w_key_prob_gt_threshold[0])

            song_key_pred_for_each_event = self.event_key_preds_dict[songname]
            key_segments = get_key_segments_from_consecutive_idx_groups(song_key_pred_for_each_event, consecutive_idx_groups)

            key_segment_indices_dict[songname] = key_segments

        return key_segment_indices_dict

class ThresholdedMicchiModelComparator:

    def __init__(self, thresholded_micchi_model, clear_key_segment_excluded_events_npz_path,
                 threshold):
        """

        Parameters
        ----------
        thresholded_micchi_model : ThresholdedMicchiModel
        clear_key_segment_excluded_events_npz_path : str
        threshold : float
        """
        self.thresholded_micchi_model = thresholded_micchi_model
        self.thresholded_micchi_model.update_threshold(threshold)

        npz_file_handler = NpzFileHandler()
        self.clear_key_segment_excluded_events_dict = npz_file_handler.read_npz_file(clear_key_segment_excluded_events_npz_path)

    def get_threshold_included_events_dict(self):
        """
        """
        threshold_included_events_dict = {}
        for songname in self.thresholded_micchi_model.event_key_probs_dict:
            song_event_key_probs = self.thresholded_micchi_model.event_key_probs_dict[songname]
            song_max_key_prob_for_each_event = self.thresholded_micchi_model.compute_max_key_prob_for_each_event(song_event_key_probs)
            threshold_included_events = self.mark_events_w_prob_greater_than_or_equal_to_threshold(song_max_key_prob_for_each_event)
            threshold_included_events_dict[songname] = threshold_included_events

        return threshold_included_events_dict

    def mark_events_w_prob_greater_than_or_equal_to_threshold(self, song_max_key_prob_for_each_event):
        """

        Parameters
        ----------
        song_max_key_prob_for_each_event : np.ndarray
        """
        return (song_max_key_prob_for_each_event >= self.thresholded_micchi_model.threshold)

    def find_overlapping_events(self):
        """
        """
        threshold_included_events_dict = self.get_threshold_included_events_dict()

        num_overlapping_events = 0
        total_num_events = 0
        for songname in threshold_included_events_dict:
            song_clear_key_segment_included_events = np.logical_not(self.clear_key_segment_excluded_events_dict[songname])
            song_threshold_included_events = threshold_included_events_dict[songname]
            num_overlapping_events += np.sum(song_clear_key_segment_included_events * song_threshold_included_events)
            total_num_events += song_threshold_included_events.shape[0]

        overlapping_events_percentage = (num_overlapping_events / total_num_events) * 100.0
        print("Overlapping events percentage (threshold: {:.3f}): {:.4f}% ({}/{})".format(self.thresholded_micchi_model.threshold,
                                                                                          overlapping_events_percentage,
                                                                                          num_overlapping_events, total_num_events))

class AccuracyAndCoveragePlotter:

    def __init__(self, thresholds, coverages, accuracies):
        """
        """
        self.thresholds = thresholds
        self.coverages = coverages
        self.accuracies = accuracies

    def plot_accuracy_and_coverage_vs_threshold(self):
        """
        """
        fig, ax = plt.subplots()

        plt.xlim(0.0, 1.05)
        plt.ylim(0.0, 102.0)

        ax.scatter(self.thresholds, self.coverages, label='Coverage')
        ax.scatter(self.thresholds, self.accuracies, c='#ff7f0e', label='Accuracy')

        legend = ax.legend(loc='lower left', shadow=True, fontsize='small')

        plot_title = self.get_plot_title()
        plt.title(plot_title)
        plt.xlabel("Threshold")
        plt.ylabel("Coverage and Accuracy")

        output_plot_filename = self.get_output_plot_filename()
        plt.savefig(output_plot_filename)

    def get_plot_title(self):
        """
        """
        return "Coverage and Accuracy vs. Threshold" 

    def get_output_plot_filename(self):
        """
        """
        return "out/plots/micchi_model2021_accuracy_and_coverage_vs_threshold"

def compute_accuracy_and_coverage_for_all_thresholds(thresholded_micchi_model,
                                                     thresholds,
                                                     generate_plots=False):
    """
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

    if generate_plots:
        acc_and_coverage_plotter = AccuracyAndCoveragePlotter(thresholds, coverages, accuracies)
        acc_and_coverage_plotter.plot_accuracy_and_coverage_vs_threshold()

def compute_fragmentation_for_all_thresholds(thresholded_micchi_model,
                                             thresholds,
                                             generate_plots=False):
    """
    """
    print("\nFragmentation:")
    for threshold in thresholds:
        thresholded_micchi_model.update_threshold(threshold)

        key_segment_indices_dict = thresholded_micchi_model.get_key_segment_indices_dict()

        fragmentation_computer = FragmentationComputer(key_segment_indices_dict,
                                                       threshold)
        fragmentation_computer.compute_and_output_avg_segment_len()
        segment_length_to_frequency_dict = fragmentation_computer.compute_segment_length_to_frequency_dict()

        if generate_plots:
            segment_length_to_frequency_plotter = SegmentLengthToFrequencyPlotter(segment_length_to_frequency_dict,
                                                                                  threshold)
            segment_length_to_frequency_plotter.plot_segment_length_to_frequency_scatter()
    print()

def compute_whole_key_segment_acc_for_all_thresholds(thresholded_micchi_model,
                                                     thresholds):
    """
    """
    for threshold in thresholds:
        thresholded_micchi_model.update_threshold(threshold)
        print("Threshold:", threshold)

        key_segment_indices_dict = thresholded_micchi_model.get_key_segment_indices_dict()

        whole_segment_key_acc_computer = WholeSegmentKeyAccuracyComputer(thresholded_micchi_model.event_key_preds_dict,
                                                                         thresholded_micchi_model.ground_truth_key_labels_dict,
                                                                         key_segment_indices_dict)

        whole_segment_key_acc_computer.compute_whole_segment_key_accuracies_for_all_songs()
        whole_segment_key_acc_computer.compute_fragmentation_for_all_songs()

def get_commandline_args():
    """
    Returns
    -------
    commandline_args : argparse.Namespace
    """
    parser = ArgumentParser(description='')
    parser.add_argument('--event_key_probs_npz_path', type=str,
                        help='Path to .npz file containing the event key '
                             'probabilities outputted by the Micchi model.')
    parser.add_argument('--ground_truth_key_labels_npz_path', type=str,
                        help='Path to .npz file containing the ground '
                             'truth key labels for the same songs as '
                             '`--event_key_probs_npz_path`.')

    parser.add_argument('--compare_threshold_key_segments_against_clear_key_segments',
                        action='store_true')
    parser.add_argument('--clear_key_segment_excluded_events_npz_path', type=str,
                        help='Only relevant if '
                             '`--compare_threshold_key_segments_against_clear_key_segments`'
                             'chosen. Path to .npz file containing the events '
                             'that should be ignored in the same songs as '
                             '`--event_key_probs_npz_path`. Indicates which '
                             'events are included in the clear key segments.')

    parser.add_argument('--generate_plots', action='store_true')

    commandline_args = parser.parse_args()

    return commandline_args

if __name__ == '__main__':
    args = get_commandline_args()
    print(args)

    npz_file_handler = NpzFileHandler()
    event_key_probs_dict = npz_file_handler.read_npz_file(args.event_key_probs_npz_path)
    ground_truth_key_labels_dict = npz_file_handler.read_npz_file(args.ground_truth_key_labels_npz_path)

    generate_plots = args.generate_plots
    compare_threshold_key_segments_against_clear_key_segments = args.compare_threshold_key_segments_against_clear_key_segments
    clear_key_segment_excluded_events_npz_path = args.clear_key_segment_excluded_events_npz_path

    thresholds = [0.98, 0.89, 0.875, 0.87, 0.865, 0.825, 0.81, 0.51, 0.17] #list(np.arange(0.1, 1.0, 0.005))
    thresholded_micchi_model = ThresholdedMicchiModel(event_key_probs_dict, ground_truth_key_labels_dict)

    compute_accuracy_and_coverage_for_all_thresholds(thresholded_micchi_model,
                                                     thresholds,
                                                     generate_plots)

    compute_fragmentation_for_all_thresholds(thresholded_micchi_model,
                                             thresholds,
                                             generate_plots)

    compute_whole_key_segment_acc_for_all_thresholds(thresholded_micchi_model,
                                                     thresholds)

    if compare_threshold_key_segments_against_clear_key_segments: 
        for threshold in thresholds:
            thresholded_micchi_model_comparator = ThresholdedMicchiModelComparator(thresholded_micchi_model,
                                                                                   clear_key_segment_excluded_events_npz_path,
                                                                                   threshold)
            thresholded_micchi_model_comparator.find_overlapping_events()