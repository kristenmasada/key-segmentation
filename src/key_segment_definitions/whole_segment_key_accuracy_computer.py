"""
"""

from matplotlib import pyplot as plt
import numpy as np

from fragmentation_computer import FragmentationComputer
from accuracy_computer_utils import compute_key_segment_length, \
                                    truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels

class SongWholeSegmentKeyAccuracyComputer:

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
        self.event_key_predictions = micchi_model_event_key_predictions
        self.ground_truth_event_key_labels = ground_truth_event_key_labels

        self.event_key_predictions = truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels(
                                                                          self.event_key_predictions,
                                                                          self.ground_truth_event_key_labels)

        self.key_segment_indices = key_segment_indices

        self.verbose = verbose

    def get_correct_whole_segments(self):
        """
        """
        correct_whole_segments = []
        for key_segment_idx in self.key_segment_indices:
            start_idx, stop_idx = key_segment_idx[0], key_segment_idx[1]
            pred_event_key_segment_labels = self.event_key_predictions[start_idx:stop_idx]
            ground_truth_event_key_segment_labels = self.ground_truth_event_key_labels[start_idx:stop_idx]

            if np.all(pred_event_key_segment_labels == ground_truth_event_key_segment_labels):
                correct_whole_segments.append(key_segment_idx)

        return correct_whole_segments

    def compute_whole_segment_key_accuracy_stats(self, correct_whole_key_segment_indices):
        """

        Parameters
        ----------
        correct_whole_key_segment_indices : 
        """
        song_num_correct_whole_segments = len(correct_whole_key_segment_indices) 
        song_num_segments = len(self.key_segment_indices) 

        song_num_correct_whole_segment_events = self.compute_num_events_in_segments(correct_whole_key_segment_indices) 
        song_num_segment_events = self.compute_num_events_in_segments(self.key_segment_indices)

        return song_num_correct_whole_segments, song_num_segments, \
               song_num_correct_whole_segment_events, song_num_segment_events

    def compute_num_events_in_segments(self, key_segments):
        """
        """
        num_segment_events = 0
        for key_segment in key_segments:
            num_segment_events += compute_key_segment_length(key_segment)

        return num_segment_events

    def compute_and_output_whole_segment_key_accuracies(self, song_num_correct_whole_segments, song_num_segments,
                                                        song_num_correct_whole_segment_events, song_num_segment_events):
        """
        """
        if song_num_segments == 0:
            percentage_correct_whole_segments = 0
        else:
            percentage_correct_whole_segments = (song_num_correct_whole_segments / song_num_segments) * 100.0

        print("Percentage of segments that are entirely correct (by segments): {}% ({}/{})".format(percentage_correct_whole_segments, song_num_correct_whole_segments, song_num_segments))

        if song_num_segment_events == 0:
            percentage_correct_whole_segment_events = 0
        else:
            percentage_correct_whole_segment_events = (song_num_correct_whole_segment_events / song_num_segment_events) * 100.0

        print("Percentage of segments that are entirely correct (by events): {}% ({}/{})".format(percentage_correct_whole_segment_events, song_num_correct_whole_segment_events, song_num_segment_events))

class WholeSegmentKeyAccuracyComputer:

    def __init__(self, song_event_key_preds_dict, ground_truth_key_labels_dict,
                 key_segment_indices_dict, verbose=False):
        """

        Parameters
        ----------
        song_event_key_preds_dict : dict of { str : np.ndarray (dtype='float32')}
        ground_truth_key_labels_dict : dict of { str : np.ndarray (dtype='int64')}
        key_segment_indices_dict : dict of { str : np.ndarray (dtype='int64')}
        verbose : bool
        """
        self.song_event_key_preds_dict = song_event_key_preds_dict

        self.ground_truth_key_labels_dict = ground_truth_key_labels_dict
        self.key_segment_indices_dict = key_segment_indices_dict

        self.overall_num_correct_whole_segments = 0
        self.overall_num_segments = 0

        self.overall_num_correct_whole_segment_events = 0
        self.overall_num_segment_events = 0

        self.verbose = verbose

        self.correct_whole_key_segments_dict = {}

    def compute_whole_segment_key_accuracies_for_each_song(self):
        """
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

            song_whole_segment_key_accuracy_computer = SongWholeSegmentKeyAccuracyComputer(
                                                                song_event_key_preds,
                                                                song_gt_key_labels,
                                                                song_key_segment_indices,
                                                                self.verbose)

            correct_whole_key_segments = song_whole_segment_key_accuracy_computer.get_correct_whole_segments()

            self.correct_whole_key_segments_dict[songname] = correct_whole_key_segments 

            song_num_correct_whole_segments, \
            song_num_segments, \
            song_num_correct_whole_segment_events, \
            song_num_segment_events = song_whole_segment_key_accuracy_computer.compute_whole_segment_key_accuracy_stats(correct_whole_key_segments)

            if self.verbose:
                song_whole_segment_key_accuracy_computer.compute_and_output_whole_segment_key_accuracies(
                                                                    song_num_correct_whole_segments,
                                                                    song_num_segments,
                                                                    song_num_correct_whole_segment_events,
                                                                    song_num_segment_events)

            self.overall_num_correct_whole_segments += song_num_correct_whole_segments
            self.overall_num_segments += song_num_segments
            self.overall_num_correct_whole_segment_events += song_num_correct_whole_segment_events
            self.overall_num_segment_events += song_num_segment_events

    def compute_whole_segment_key_accuracies_for_all_songs(self):
        """
        """
        self.compute_whole_segment_key_accuracies_for_each_song()

        overall_whole_segment_acc = (self.overall_num_correct_whole_segments / self.overall_num_segments) * 100.0
        print("\nOverall whole segment accuracy {:.1f}% ({}/{})".format(overall_whole_segment_acc,
                                                                        self.overall_num_correct_whole_segments,
                                                                        self.overall_num_segments))

        overall_whole_segment_event_acc = (self.overall_num_correct_whole_segment_events / self.overall_num_segment_events) * 100.0
        print("Overall whole segment event accuracy {:.1f}% ({}/{})".format(overall_whole_segment_event_acc,
                                                                            self.overall_num_correct_whole_segment_events,
                                                                            self.overall_num_segment_events))
        print()

    def compute_fragmentation_for_all_songs(self):
        """
        """
        fragmentation_computer = FragmentationComputer(self.correct_whole_key_segments_dict)
        fragmentation_computer.compute_and_output_avg_segment_len()