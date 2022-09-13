""" Compute the event-level key accuracy for each song.
Also compute and output the overall event-level key accuracy.
"""

from argparse import ArgumentParser

import numpy as np

from file_handlers import NpzFileHandler
from utils import exclude_events_outside_of_key_segments_from_event_key_labels, \
                  truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels

class SongEventKeyAccuracyComputer:
    """ Compute the event-level key accuracy for one song.
    """

    def __init__(self, micchi_model_event_key_predictions, ground_truth_event_key_labels,
                 key_segment_indices, verbose=False):
        """

        Parameters
        ----------
        micchi_model_event_key_predictions : np.ndarray (dtype='float32', shape=(no. events,))
        ground_truth_event_key_labels : np.ndarray (dtype='int64', shape=(no. events,))
            Each element is the index of the key prediction for that event.
        key_segment_indices : np.ndarray (dtype='int64', shape=(no. key segments, 2))
        verbose : bool
        """
        self.ground_truth_event_key_labels = ground_truth_event_key_labels
        self.event_key_predictions = micchi_model_event_key_predictions

        self.event_key_predictions = truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels(
                                                                          self.event_key_predictions,
                                                                          self.ground_truth_event_key_labels)

        if key_segment_indices is not None:
            self.ground_truth_event_key_labels = exclude_events_outside_of_key_segments_from_event_key_labels(
                                                                           self.ground_truth_event_key_labels,
                                                                                          key_segment_indices)
            self.event_key_predictions = exclude_events_outside_of_key_segments_from_event_key_labels(
                                                                            self.event_key_predictions,
                                                                                    key_segment_indices)

        self.verbose = verbose

    def compute_key_event_level_accuracy_stats(self):
        """ Compute the number of correct events and the
        total number of events in the song.
        """
        num_correct_events = np.sum(self.event_key_predictions == self.ground_truth_event_key_labels)
        total_num_events = self.ground_truth_event_key_labels.shape[0]
        return num_correct_events, total_num_events

    def compute_key_event_level_accuracy(self, num_correct_events, total_num_events):
        """ Compute the event-level key accuracy for one song.

        Parameters
        ----------
        num_correct_events : int
        total_num_events : int
        """
        if total_num_events == 0:
            if self.verbose:
                print("Warning: total no. events computed as 0.\n")
            return 0

        event_level_accuracy = (num_correct_events / total_num_events) * 100.0

        if self.verbose:
            print("Event-level key accuracy: {:.4f}% ({}/{})".format(event_level_accuracy, num_correct_events, total_num_events))
            print()

        return event_level_accuracy

class EventKeyAccuracyComputer:    
    """ Compute the event-level key accuracy for all songs.
    """

    def __init__(self, song_event_key_preds_dict, ground_truth_key_labels_dict,
                 key_segment_indices_dict, use_majority_key_segment_labeling=False,
                 verbose=False):
        """

        Parameters
        ----------
        song_event_key_preds_dict : dict of { str : np.ndarray (dtype='float32') }
        ground_truth_key_labels_dict : dict of { str : np.ndarray (dtype='int64') }
        key_segment_indices_dict : dict of { str : np.ndarray (dtype='int64') }
        use_majority_key_segment_labeling : bool
        verbose : bool
        """
        assert song_event_key_preds_dict.keys() == ground_truth_key_labels_dict.keys()

        self.song_event_key_preds_dict = song_event_key_preds_dict

        self.ground_truth_key_labels_dict = ground_truth_key_labels_dict
        self.key_segment_indices_dict = key_segment_indices_dict

        self.overall_num_correct_events = 0
        self.overall_total_num_events = 0

        self.use_majority_key_segment_labeling = use_majority_key_segment_labeling
        
        self.verbose = verbose

    def check_songnames_in_key_predictions_vs_ground_truth_labels(self):
        """ For debugging: output if there are any songs in
        `self.song_event_key_preds_dict` that aren't in `self.ground_truth_key_labels_dict`,
        and vice versa.
        """
        print()
        print("Songs in `self.song_event_key_preds_dict` that aren't in `self.ground_truth_key_labels_dict`:")
        print(set(self.song_event_key_preds_dict.keys()) - set(self.ground_truth_key_labels_dict.keys()))
        print()
        print("Songs in `self.ground_truth_key_labels_dict` that aren't in `self.song_event_key_preds_dict`:")
        print(set(self.ground_truth_key_labels_dict.keys()) - set(self.song_event_key_preds_dict.keys()))

    def compute_event_level_key_accuracy_for_each_song(self):
        """ Compute the event-level key accuracy for each song.
        """
        for songname in self.song_event_key_preds_dict: 

            if self.verbose:
                print("Song:", songname)

            song_event_key_preds = self.song_event_key_preds_dict[songname]
            song_gt_key_labels = self.ground_truth_key_labels_dict[songname]

            if self.key_segment_indices_dict:
                if songname not in self.key_segment_indices_dict:
                    print("Error: {} not in self.key_segment_indices_dict\n".format(songname))
                    continue
                else:
                    song_key_segment_indices = self.key_segment_indices_dict[songname]
            else:
                song_key_segment_indices = None

            song_event_key_accuracy_computer = SongEventKeyAccuracyComputer(song_event_key_preds,
                                                                            song_gt_key_labels,
                                                                            song_key_segment_indices,
                                                                            self.use_majority_key_segment_labeling,
                                                                            self.verbose)

            song_num_correct_events, \
            song_total_num_events = song_event_key_accuracy_computer.compute_key_event_level_accuracy_stats()

            song_event_key_accuracy_computer.compute_key_event_level_accuracy(song_num_correct_events,
                                                                              song_total_num_events)

            self.overall_num_correct_events += song_num_correct_events
            self.overall_total_num_events += song_total_num_events

    def compute_event_level_key_accuracy_for_all_songs(self):
        """ Compute the event-level key accuracy for each song.
        Also compute and output the overall event-level key accuracy.
        """
        self.compute_event_level_key_accuracy_for_each_song()

        overall_event_level_accuracy = (self.overall_num_correct_events / self.overall_total_num_events) * 100.0
        print("Overall event-level accuracy {:.4f}% ({}/{})".format(overall_event_level_accuracy, self.overall_num_correct_events,
                                                                    self.overall_total_num_events))
        print()

        return self.overall_num_correct_events, self.overall_total_num_events 

def get_commandline_args():
    """ Get commandline argument values from user.
    """
    parser = ArgumentParser(description='')
    parser.add_argument('--event_key_preds_npz_path', type=str,
                        help='Path to .npz file containing the event key '
                             'predictions.')
    parser.add_argument('--ground_truth_key_labels_npz_path', type=str,
                        help='Path to .npz file containing the ground '
                             'truth key labels for the same songs as in '
                             '`--event_key_preds_npz_path`.')
    parser.add_argument('--key_segment_indices_npz_path', type=str,
                        help='Path to .npz file containing the events '
                             'that should be ignored in the same songs as '
                             '`--event_key_preds_npz_path`. Can be used '
                             'to exclude tonicizations, exclude events '
                             'that don\'t belong to our key definition, etc.')

    commandline_args = parser.parse_args()

    return commandline_args

if __name__ == '__main__':
    args = get_commandline_args()
    print(args)

    npz_file_handler = NpzFileHandler()
    song_event_key_preds_dict = npz_file_handler.read_npz_file(args.event_key_preds_npz_path)
    ground_truth_key_labels_dict = npz_file_handler.read_npz_file(args.ground_truth_key_labels_npz_path)

    if args.key_segment_indices_npz_path is not None:
        key_segment_indices_dict = npz_file_handler.read_npz_file(args.key_segment_indices_npz_path)
    else:
        key_segment_indices_dict = None

    event_level_acc_computer = EventKeyAccuracyComputer(song_event_key_preds_dict,
                                                        ground_truth_key_labels_dict,
                                                        key_segment_indices_dict)
    event_level_acc_computer.compute_event_level_key_accuracy_for_all_songs()