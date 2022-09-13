""" Compute the results included in Table 6.1 of thesis for key
segments generated using one of the 9 clear key segment definitions
(Accuracy w.r.t. true boundaries [TB] and system boundaries [SB];
Precision and Recall with respect to the ground truth C-KS;
Recall with respect to the complete piece; Coverage is the
proportion of a complete piece covered by predicted C-KS).
"""

from argparse import ArgumentParser

from clear_key_precision_recall_computer import ClearKeyPrecisionRecallComputer
from complete_piece_recall_coverage_computer import CompletePieceRecallCoverageComputer
from event_key_accuracy_computer import EventKeyAccuracyComputer
from file_handlers import NpzFileHandler
from utils import convert_one_hot_vector_events_to_event_key_labels, \
                  remove_songs_to_ignore_from_dict
from whole_segment_key_accuracy_computer import WholeSegmentKeyAccuracyComputer

class KeyIdentificationStatsComputer:
    """ Compute the results included in Table 6.1 of thesis for key
    segments generated using one of the 9 clear key segment definitions
    (Accuracy w.r.t. true boundaries [TB] and system boundaries [SB];
    Precision and Recall with respect to the ground truth C-KS;
    Recall with respect to the complete piece; Coverage is the
    proportion of a complete piece covered by predicted C-KS).
    """

    def __init__(self, song_event_key_preds_dict, ground_truth_key_labels_dict,
                 predicted_key_segment_indices_dict,
                 ground_truth_key_segment_indices_dict,
                 verbose=False):
        """

        Parameters
        ----------
        song_event_key_preds_dict : dict of { str : np.ndarray (dtype='float32', shape=(no. events, 24 keys)) }
            Each event is a one-hot vector.
        ground_truth_key_labels_dict : dict of { str : np.ndarray (dtype='int64', shape=(no. events,)) }
            Each event is the ground truth key label (i.e. a number in the range [0, 23]) for that event.
        predicted_key_segment_indices_dict : dict of { str : np.ndarray (dtype='int64', shape=(no. key segments, 2)) }
            Each row contains the start and end event index of each key segment.
        ground_truth_key_segment_indices_dict : dict of { str : np.ndarray (dtype='int64', shape=(no. key segments, 2)) }
            Each row contains the start and end event index of each key segment.
        verbose : bool
        """
        self.songs_to_ignore = ["Mozart_Wolfgang_Amadeus_-___-_K455"]

        self.song_event_key_pred_labels_dict = convert_one_hot_vector_events_to_event_key_labels(song_event_key_preds_dict)
        self.song_event_key_pred_labels_dict = remove_songs_to_ignore_from_dict(self.songs_to_ignore, self.song_event_key_pred_labels_dict)
        self.ground_truth_key_labels_dict = remove_songs_to_ignore_from_dict(self.songs_to_ignore, ground_truth_key_labels_dict)

        if predicted_key_segment_indices_dict is not None:
            self.predicted_key_segment_indices_dict = remove_songs_to_ignore_from_dict(self.songs_to_ignore, predicted_key_segment_indices_dict)
        else:
            self.predicted_key_segment_indices_dict = None 

        if ground_truth_key_segment_indices_dict is not None:
            self.ground_truth_key_segment_indices_dict = remove_songs_to_ignore_from_dict(self.songs_to_ignore, ground_truth_key_segment_indices_dict)
        else:
            self.ground_truth_key_segment_indices_dict = None

        self.verbose = verbose

    def compute_stats(self):
        """ Compute the results included in Table 6.1 of thesis for key
        segments generated using one of the 9 clear key segment definitions.
        """
        print("True boundaries accuracy:")
        ground_truth_event_key_acc_computer = EventKeyAccuracyComputer(self.song_event_key_pred_labels_dict,
                                                                       self.ground_truth_key_labels_dict,
                                                                       self.ground_truth_key_segment_indices_dict,
                                                                       self.verbose)
        ground_truth_event_key_acc_computer.compute_event_level_key_accuracy_for_all_songs()

        print("System boundaries accuracy:")
        predicted_event_key_acc_computer = EventKeyAccuracyComputer(self.song_event_key_pred_labels_dict,
                                                                    self.ground_truth_key_labels_dict,
                                                                    self.predicted_key_segment_indices_dict,
                                                                    verbose=self.verbose)
        num_correctly_predicted_events, \
        num_events_in_predicted_segments = predicted_event_key_acc_computer.compute_event_level_key_accuracy_for_all_songs()

        print("Clear key segments precision and recall:")
        clear_key_precision_recall_computer = ClearKeyPrecisionRecallComputer(self.song_event_key_pred_labels_dict,
                                                                              self.ground_truth_key_labels_dict,
                                                                              self.ground_truth_key_segment_indices_dict,
                                                                              self.predicted_key_segment_indices_dict,
                                                                              self.verbose)
        clear_key_precision_recall_computer.compute_precision_and_recall_for_all_songs()

        print("Complete piece recall and coverage:")
        complete_piece_recall_coverage_computer = CompletePieceRecallCoverageComputer(num_correctly_predicted_events,
                                                                                      num_events_in_predicted_segments,
                                                                                      self.ground_truth_key_labels_dict)
        complete_piece_recall_coverage_computer.compute_and_output_recall_and_coverage()

        if self.predicted_key_segment_indices_dict is None:
            self.predicted_key_segment_indices_dict = self.get_predicted_key_segment_indices_dict_for_all_events() 

        whole_segment_key_acc_computer = WholeSegmentKeyAccuracyComputer(self.song_event_key_pred_labels_dict,
                                                                         self.ground_truth_key_labels_dict,
                                                                         self.predicted_key_segment_indices_dict,
                                                                         self.verbose)
        whole_segment_key_acc_computer.compute_whole_segment_key_accuracies_for_all_songs()
        whole_segment_key_acc_computer.compute_fragmentation_for_all_songs()

    def get_predicted_key_segment_indices_dict_for_all_events(self):
        """ Get key segment eighth note beat start and stop indices
        for each song for Clear Key Segment Definition 9 in thesis,
        where a key segment is the complete musical input (i.e.
        there should only be one key segment per song, where the
        start index is 0 and the stop index is the number of events
        in the song).
        """
        predicted_key_segment_indices_dict = {}
        for songname in self.ground_truth_key_labels_dict:
            gt_key_labels = self.ground_truth_key_labels_dict[songname]
            num_song_events = gt_key_labels.shape[0] 
            predicted_key_segment_indices_dict[songname] = [[0, num_song_events]]

        return predicted_key_segment_indices_dict

def get_commandline_args():
    """ Get commandline arguments from user.
    """
    parser = ArgumentParser(description='Compute the results included in Table 6.1 of thesis for key '
                                        'segments generated using one of the 9 clear key segment definitions.')
    parser.add_argument('--event_key_preds_npz_path', type=str,
                        help='Path to .npz file containing the event key '
                             'predictions for all of the events in a song.')
    parser.add_argument('--ground_truth_key_labels_npz_path', type=str,
                        help='Path to .npz file containing the ground '
                             'truth key labels for the same songs as '
                             '`--event_key_preds_npz_path`.')
    parser.add_argument('--predicted_key_segment_indices_npz_path', type=str,
                        help='Path to .npz file containing the indices of '
                              'the events that should be included in each '
                              'predicted clear key segment.')
    parser.add_argument('--ground_truth_key_segment_indices_npz_path', type=str,
                        help='Path to .npz file containing the indices of '
                              'the events that should be included in each '
                              'ground truth clear key segment.')
    commandline_args = parser.parse_args()

    return commandline_args

if __name__ == '__main__':
    args = get_commandline_args()
    print(args)

    npz_file_handler = NpzFileHandler()
    song_event_key_preds_dict = npz_file_handler.read_npz_file(args.event_key_preds_npz_path)
    ground_truth_key_labels_dict = npz_file_handler.read_npz_file(args.ground_truth_key_labels_npz_path)

    if args.predicted_key_segment_indices_npz_path:
        predicted_key_segment_indices_dict = npz_file_handler.read_npz_file(args.predicted_key_segment_indices_npz_path)
    else:
        predicted_key_segment_indices_dict = None

    if args.ground_truth_key_segment_indices_npz_path:
        ground_truth_key_segment_indices_dict = npz_file_handler.read_npz_file(args.ground_truth_key_segment_indices_npz_path)
    else:
        ground_truth_key_segment_indices_dict = None

    key_identification_stats_computer = KeyIdentificationStatsComputer(song_event_key_preds_dict,
                                                                       ground_truth_key_labels_dict,
                                                                       predicted_key_segment_indices_dict,
                                                                       ground_truth_key_segment_indices_dict)
    key_identification_stats_computer.compute_stats()