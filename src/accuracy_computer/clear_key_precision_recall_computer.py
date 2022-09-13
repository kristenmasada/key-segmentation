""" Compute the clear key precision and recall for each song
and for all songs overall.
"""

from argparse import ArgumentParser

import numpy as np

from file_handlers import NpzFileHandler
from utils import convert_key_indices_to_excluded_events_vector, \
                  exclude_specified_events_from_event_key_labels, \
                  truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels 

class SongClearKeyPrecisionRecallComputer:
    """ Compute the clear key precision and recall for one song.
    """

    def __init__(self, micchi_model_event_key_predictions, ground_truth_event_key_labels,
                 ground_truth_key_segment_indices, predicted_key_segment_indices,
                 verbose=False):
        """

        Parameters
        ----------
        micchi_model_event_key_predictions : np.ndarray (dtype='float32', shape=(no. song events,))
        ground_truth_event_key_labels : np.ndarray (dtype='int64', shape=(no. song events,))
        ground_truth_key_segment_indices : np.ndarray (dtype='int64', shape=(no. key segments, 2))
            For each ground truth key segment, the first element is eighth note beat start index
            and second element is the eighth note beat stop index.
        predicted_key_segment_indices : np.ndarray (dtype='int64', shape=(no. key segments, 2))
            For each predicted key segment, the first element is eighth note beat start index
            and second element is the eighth note beat stop index.
        verbose : bool
        """
        self.event_key_predictions = micchi_model_event_key_predictions
        self.ground_truth_event_key_labels = ground_truth_event_key_labels

        self.event_key_predictions = truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels(
                                                                          self.event_key_predictions,
                                                                          self.ground_truth_event_key_labels)

        num_events = self.ground_truth_event_key_labels.shape[0]
        ground_truth_key_segment_excluded_events = convert_key_indices_to_excluded_events_vector(ground_truth_key_segment_indices,
                                                                                                 num_events) 
        predicted_key_segment_excluded_events = convert_key_indices_to_excluded_events_vector(predicted_key_segment_indices,
                                                                                              num_events)

        # NOTE: Make it so that events that shouldn't be excluded (i.e. events inside key segments) = 1,
        # and events that should be excluded = 0.
        self.ground_truth_key_segment_included_events = np.logical_not(ground_truth_key_segment_excluded_events)
        self.predicted_key_segment_included_events = np.logical_not(predicted_key_segment_excluded_events)

        # NOTE: here, events that should be excluded = 1, and events that shouldn't be = 0
        # (opposite of above).
        self.overlapping_key_segment_events = self.find_events_overlapping_ground_truth_and_predicted_key_segments()

        self.overlapping_ground_truth_event_key_labels = exclude_specified_events_from_event_key_labels(
                                                                     self.ground_truth_event_key_labels,
                                                                    self.overlapping_key_segment_events)
        self.overlapping_event_key_predictions = exclude_specified_events_from_event_key_labels(
                                                                     self.event_key_predictions,
                                                            self.overlapping_key_segment_events)

        self.verbose = verbose

    def find_events_overlapping_ground_truth_and_predicted_key_segments(self):
        """ Find events that occur both inside the ground truth and predicted
        key segments.
        """
        overlapping_key_segment_events = self.ground_truth_key_segment_included_events * self.predicted_key_segment_included_events

        return np.logical_not(overlapping_key_segment_events)

    def compute_key_precision_recall_stats(self):
        """ Compute statistics needed to compute the clear key precision
        and recall.
        """
        num_correct_pred_events_in_gt_segments = np.sum(self.overlapping_ground_truth_event_key_labels == self.overlapping_event_key_predictions)
        total_num_pred_events = np.sum(self.predicted_key_segment_included_events) 
        total_num_gt_events = np.sum(self.ground_truth_key_segment_included_events)
        return num_correct_pred_events_in_gt_segments, total_num_pred_events, total_num_gt_events

    def compute_key_event_level_precision_and_recall(self, num_correct_pred_events_in_gt_segments, total_num_pred_events,
                                                     total_num_gt_events):
        """ Compute the clear key precision* and recall* for a single song.

        *Precision is computed as follows:
        (no. predicted events that are correct AND overlap with a ground truth segment) / (total no. events in predicted segments)

        *Recall is computed as follows:
        (no. predicted events that are correct AND overlap with a ground truth segment) / (total no. events in ground truth segments)

        Parameters
        ----------
        num_correct_pred_events_in_gt_segments : int
        total_num_pred_events : int
        total_num_gt_events : int 
        """
        if total_num_pred_events == 0:
            song_precision = 0
            if self.verbose:
                print("Warning: total no. predicted events computed as 0.\n")
        else:
            song_precision = (num_correct_pred_events_in_gt_segments / total_num_pred_events) * 100.0

        if total_num_gt_events == 0:
            song_recall = 0
            if self.verbose:
                print("Warning: total no. ground truth events computed as 0.\n")
        else:
            song_recall = (num_correct_pred_events_in_gt_segments / total_num_gt_events) * 100.0

        if self.verbose:
            print("Song precision: {:.4f}% ({}/{})".format(song_precision, num_correct_pred_events_in_gt_segments, total_num_pred_events))
            print("Song recall: {:.4f}% ({}/{})".format(song_recall, num_correct_pred_events_in_gt_segments, total_num_gt_events))
            print()

        return song_precision, song_recall

class ClearKeyPrecisionRecallComputer:    
    """ Compute the clear key precision and recall for each song.
    Also compute and output the overall clear key precision and recall.
    """

    def __init__(self, song_event_key_preds_dict, ground_truth_key_labels_dict,
                 ground_truth_key_segment_excluded_events, predicted_key_segment_excluded_events,
                 verbose=False):
        """

        Parameters
        ----------
        song_event_key_preds_dict : dict of { str : np.ndarray (dtype='float32')}
        ground_truth_key_labels_dict : dict of { str : np.ndarray (dtype='int64')}
        ground_truth_key_segment_excluded_events : dict of { str : np.ndarray }
        predicted_key_segment_excluded_events : { str : np.ndarray }
        verbose : bool
        """
        assert song_event_key_preds_dict.keys() == ground_truth_key_labels_dict.keys()

        self.song_event_key_preds_dict = song_event_key_preds_dict

        self.ground_truth_key_labels_dict = ground_truth_key_labels_dict

        self.ground_truth_key_segment_excluded_events = ground_truth_key_segment_excluded_events 
        self.predicted_key_segment_excluded_events = predicted_key_segment_excluded_events 

        self.overall_num_correct_pred_events_in_gt_segments = 0
        self.overall_total_num_pred_events = 0
        self.overall_total_num_gt_events = 0

        self.verbose = verbose

    def compute_precision_and_recall_for_each_song(self):
        """ Compute the clear key precision and recall for each song.
        """
        for songname in self.song_event_key_preds_dict: 
            if self.verbose:
                print("Song:", songname)

            song_event_key_preds = self.song_event_key_preds_dict[songname]
            song_gt_key_labels = self.ground_truth_key_labels_dict[songname]

            song_gt_key_segment_events = self.ground_truth_key_segment_excluded_events[songname]
            song_predicted_key_segment_excluded_events = self.predicted_key_segment_excluded_events[songname]

            song_key_precision_recall_computer = SongClearKeyPrecisionRecallComputer(song_event_key_preds,
                                                                                     song_gt_key_labels,
                                                                                     song_gt_key_segment_events,
                                                                                     song_predicted_key_segment_excluded_events)

            num_correct_pred_events_in_gt_segments, \
            total_num_pred_events, \
            total_num_gt_events = song_key_precision_recall_computer.compute_key_precision_recall_stats()

            song_key_precision_recall_computer.compute_key_event_level_precision_and_recall(num_correct_pred_events_in_gt_segments,
                                                                                            total_num_pred_events,
                                                                                            total_num_gt_events)

            self.overall_num_correct_pred_events_in_gt_segments += num_correct_pred_events_in_gt_segments 
            self.overall_total_num_pred_events += total_num_pred_events
            self.overall_total_num_gt_events += total_num_gt_events

    def compute_precision_and_recall_for_all_songs(self):
        """ Compute the clear key precision and recall for each song.
        Also compute and output the overall clear key precision and recall.
        """
        self.compute_precision_and_recall_for_each_song()

        overall_precision = (self.overall_num_correct_pred_events_in_gt_segments / self.overall_total_num_pred_events) * 100.0
        print("Overall precision {:.4f}% ({}/{})".format(overall_precision, self.overall_num_correct_pred_events_in_gt_segments,
                                                         self.overall_total_num_pred_events))

        overall_recall = (self.overall_num_correct_pred_events_in_gt_segments / self.overall_total_num_gt_events) * 100.0
        print("Overall recall {:.4f}% ({}/{})".format(overall_recall, self.overall_num_correct_pred_events_in_gt_segments,
                                                      self.overall_total_num_gt_events))
        print()

def get_commandline_args():
    """ Get commandline argument values from user. 
    """
    parser = ArgumentParser(description='Compute the clear key precision and recall for each song. '
                                        'Also compute these for all songs overall.')
    parser.add_argument('--event_key_preds_npz_path', type=str,
                        help='Path to .npz file containing the event key '
                             'predictions for all of the events in a song.')
    parser.add_argument('--ground_truth_key_labels_npz_path', type=str,
                        help='Path to .npz file containing the ground '
                             'truth key labels for the same songs as '
                             '`--event_key_preds_npz_path`.')
    parser.add_argument('--ground_truth_key_segment_excluded_events_npz_path', type=str,
                        help='Path to .npz file containing the events that '
                             'should be ignored to correspond with the ground '
                             'truth clear key segment events.')
    parser.add_argument('--predicted_key_segment_excluded_events_npz_path', type=str,
                        help='Path to .npz file containing the events that '
                             'should be ignored to correspond with the '
                             'predicted clear key segment events.')

    commandline_args = parser.parse_args()

    return commandline_args

if __name__ == '__main__':
    args = get_commandline_args()
    print(args)

    npz_file_handler = NpzFileHandler()
    song_event_key_preds_dict = npz_file_handler.read_npz_file(args.event_key_preds_npz_path)
    ground_truth_key_labels_dict = npz_file_handler.read_npz_file(args.ground_truth_key_labels_npz_path)
    ground_truth_key_segment_excluded_events = npz_file_handler.read_npz_file(args.ground_truth_key_segment_excluded_events_npz_path)
    predicted_key_segment_excluded_events = npz_file_handler.read_npz_file(args.predicted_key_segment_excluded_events_npz_path)

    prec_recall_computer = ClearKeyPrecisionRecallComputer(song_event_key_preds_dict,
                                                           ground_truth_key_labels_dict,
                                                           ground_truth_key_segment_excluded_events,
                                                           predicted_key_segment_excluded_events)
    prec_recall_computer.compute_precision_and_recall_for_all_songs()