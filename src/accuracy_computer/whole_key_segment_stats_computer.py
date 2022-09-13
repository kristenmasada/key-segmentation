""" Compute the statistics needed to create the whole segment
precision and recall plots (Figures 6.1-6.6 in the thesis).
"""

import numpy as np

from utils import compute_key_segment_length, \
                  get_key_segments_from_consecutive_idx_groups

class WholeKeySegmentStatsComputer:
    """ Compute the statistics needed to create the whole segment
    precision and recall plots (Figures 6.1-6.6 in the thesis).
    """

    def __init__(self, whole_segment_key_acc_computer, min_extracted_segment_count=25):
        """

        Parameters
        ----------
        whole_segment_key_acc_computer : WholeSegmentKeyAccuracyComputer
        min_extracted_segment_count : int
        """
        self.whole_segment_key_acc_computer = whole_segment_key_acc_computer

        self.predicted_segments_count_dict = self.get_segments_count_dict(self.whole_segment_key_acc_computer.key_segment_indices_dict)
        self.predicted_segments_w_min_seg_len_count_dict = self.get_min_seg_len_dict(self.predicted_segments_count_dict)
        self.sorted_cumulative_segment_len_bins = sorted(list(self.predicted_segments_w_min_seg_len_count_dict.keys()))
        self.sorted_predicted_segments_w_min_seg_len_count = self.get_sorted_segment_counts(self.sorted_cumulative_segment_len_bins,
                                                                                     self.predicted_segments_w_min_seg_len_count_dict)

        self.correct_whole_predicted_segments_count_dict = self.get_correct_whole_predicted_segments_count_dict()
        self.correct_whole_predicted_segments_w_min_seg_len_count_dict = self.get_min_seg_len_dict(self.correct_whole_predicted_segments_count_dict)
        self.sorted_correct_whole_predicted_segments_w_min_seg_len_count = self.get_sorted_segment_counts(self.sorted_cumulative_segment_len_bins,
                                                                                                          self.correct_whole_predicted_segments_w_min_seg_len_count_dict)

        self.correct_whole_predicted_segments_event_count_dict = self.get_correct_whole_predicted_segments_event_count_dict(self.correct_whole_predicted_segments_count_dict)
        self.correct_whole_predicted_segments_w_min_seg_len_event_count_dict = self.get_min_seg_len_dict(self.correct_whole_predicted_segments_event_count_dict)
        self.sorted_correct_whole_predicted_segments_w_min_seg_len_event_count = self.get_sorted_segment_counts(self.sorted_cumulative_segment_len_bins,
                                                                                                                self.correct_whole_predicted_segments_w_min_seg_len_event_count_dict)

        self.total_num_events = self.compute_total_num_events()

        self.ground_truth_key_segment_indices_dict = self.get_ground_truth_key_segment_indices_dict()
        self.ground_truth_segments_count_dict = self.get_segments_count_dict(self.ground_truth_key_segment_indices_dict)
        self.ground_truth_segments_w_min_seg_len_count_dict = self.get_min_seg_len_dict(self.ground_truth_segments_count_dict)
        self.ground_truth_segments_event_count_dict = self.get_segments_event_count_dict(self.ground_truth_key_segment_indices_dict)
        self.ground_truth_segments_w_min_seg_len_event_count_dict = self.get_min_seg_len_dict(self.ground_truth_segments_event_count_dict)

        self.min_extracted_segment_count_idx = self.find_min_extracted_segment_count_idx(min_extracted_segment_count, self.sorted_cumulative_segment_len_bins,
                                                                                         self.predicted_segments_w_min_seg_len_count_dict)

    def get_segments_count_dict(self, key_segment_indices_dict):
        """ Create a dictionary where the key is the segment length
        and the value is a count of the number of key segments
        over all songs with that length.

        Parameters
        ----------
        key_segment_indices_dict : { str : np.ndarray }
        """
        segments_count_dict = {}
        for songname in key_segment_indices_dict:
            key_segment_indices = key_segment_indices_dict[songname]
            for key_segment_idx in key_segment_indices:
                key_segment_len = compute_key_segment_length(key_segment_idx)
                if key_segment_len not in segments_count_dict:
                    segments_count_dict[key_segment_len] = 1
                else:
                    segments_count_dict[key_segment_len] += 1

        return segments_count_dict

    def get_correct_whole_predicted_segments_count_dict(self):
        """ Create a dictionary where the key is the segment length
        and the value is the number of segments with that length
        that are predicted entirely correctly. 
        """
        correct_whole_predicted_segments_count_dict = {}
        for songname in self.whole_segment_key_acc_computer.key_segment_indices_dict:
            key_segment_indices = self.whole_segment_key_acc_computer.key_segment_indices_dict[songname]
            for key_segment_idx in key_segment_indices:
                start_idx, stop_idx = key_segment_idx[0], key_segment_idx[1]
                pred_event_key_segment_labels = self.whole_segment_key_acc_computer.song_event_key_preds_dict[songname][start_idx:stop_idx]
                ground_truth_event_key_segment_labels = self.whole_segment_key_acc_computer.ground_truth_key_labels_dict[songname][start_idx:stop_idx]

                if np.all(pred_event_key_segment_labels == ground_truth_event_key_segment_labels):
                    key_segment_len = compute_key_segment_length(key_segment_idx)
                    if key_segment_len not in correct_whole_predicted_segments_count_dict:
                        correct_whole_predicted_segments_count_dict[key_segment_len] = 1
                    else:
                        correct_whole_predicted_segments_count_dict[key_segment_len] += 1

        return correct_whole_predicted_segments_count_dict

    def get_correct_whole_predicted_segments_event_count_dict(self, correct_whole_predicted_segments_count_dict):
        """ Create a dictionary where the key is the segment length and
        the value is the segment length * the total number of segments
        of that length that are predicted entirely correctly (i.e. the
        total number of events predicted correctly for that segment length).

        Parameters
        ----------
        correct_whole_predicted_segments_count_dict : dict of { int : int }
        """
        correct_whole_predicted_segments_event_count_dict = {}
        for seg_len in correct_whole_predicted_segments_count_dict:
            seg_len_count = correct_whole_predicted_segments_count_dict[seg_len]
            correct_whole_predicted_segments_event_count_dict[seg_len] = seg_len * seg_len_count

        return correct_whole_predicted_segments_event_count_dict

    def get_min_seg_len_dict(self, count_dict):
        """ Create a dictionary where the key is the segment
        length and the value is the number of key segments
        with length >= the current segment length over all
        songs.

        Parameters
        ----------
        count_dict : dict of { int : int }
        """
        min_seg_len_dict = {}

        max_key = max(count_dict.keys())
        decreasing_count_dict_keys = reversed(list(np.arange(1, max_key+1)))
        total_segments_seen_so_far = 0
        for seg_len in decreasing_count_dict_keys:
            if seg_len in count_dict:
                seg_len_count = count_dict[seg_len]
                total_segments_seen_so_far += seg_len_count

            min_seg_len_dict[seg_len] = total_segments_seen_so_far

        return min_seg_len_dict

    def get_sorted_segment_counts(self, sorted_segment_len_bins, correct_whole_segments_w_min_seg_len_count_dict):
        """ Create a list where the first element is the number of segments with
        length >= 1 that are predicted entirely correctly, the second element is
        the number of segments predicted correctly with length >= 2, and so on.

        Parameters
        ----------
        sorted_segment_len_bins : list of int
        correct_whole_segments_w_min_seg_len_count_dict : dict of { int : int }
        """
        correct_whole_segments_w_min_seg_len_count = []
        for segment_len in sorted_segment_len_bins:
            if segment_len in correct_whole_segments_w_min_seg_len_count_dict:
                correct_whole_segments_w_min_seg_len_count.append(correct_whole_segments_w_min_seg_len_count_dict[segment_len])
            else:
                correct_whole_segments_w_min_seg_len_count.append(0)

        return correct_whole_segments_w_min_seg_len_count

    def get_segments_event_count_dict(self, key_segment_indices_dict):
        """ Create a dictionary where the key is the segment length and the
        value is the count of the key segments over all songs with that
        length.

        Parameters
        ----------
        key_segment_indices_dict : { str : np.ndarray }
        """
        segments_event_count_dict = {}
        for songname in key_segment_indices_dict:
            key_segment_indices = key_segment_indices_dict[songname]
            for key_segment_idx in key_segment_indices:
                key_segment_len = compute_key_segment_length(key_segment_idx)
                if key_segment_len not in segments_event_count_dict:
                    segments_event_count_dict[key_segment_len] = key_segment_len
                else:
                    segments_event_count_dict[key_segment_len] += key_segment_len

        return segments_event_count_dict

    def compute_total_num_events(self):
        """ Compute the total number of events over all of the key
        segments over all of the songs.
        """
        total_num_events = 0
        for songname in self.whole_segment_key_acc_computer.key_segment_indices_dict:
            key_segment_indices = self.whole_segment_key_acc_computer.key_segment_indices_dict[songname]
            for key_segment_idx in key_segment_indices:
                key_segment_len = compute_key_segment_length(key_segment_idx)
                total_num_events += key_segment_len

        return total_num_events

    def get_ground_truth_key_segment_indices_dict(self):
        """ Create a dictionary where the key is the songname and the
        value is a list of the eighth note beat start and stop indices
        of the ground truth key segments.
        """
        ground_truth_key_segment_indices_dict = {}
        for songname in self.whole_segment_key_acc_computer.ground_truth_key_labels_dict:
            song_ground_truth_key_labels = self.whole_segment_key_acc_computer.ground_truth_key_labels_dict[songname]
            song_ground_truth_key_segment_indices = get_key_segments_from_consecutive_idx_groups(song_ground_truth_key_labels,
                                                                                                 [np.arange(song_ground_truth_key_labels.shape[0])])
            ground_truth_key_segment_indices_dict[songname] = song_ground_truth_key_segment_indices
            
        return ground_truth_key_segment_indices_dict

    def find_min_extracted_segment_count_idx(self, min_extracted_segment_count, sorted_cumulative_segment_len_bins,
                                             predicted_segments_w_min_seg_len_count_dict):
        """ Find the point at which at least `min_extracted_segment_count` segments
        have been predicted (`min_extracted_segment_count` is usually set to 25).
        This information is later used to place a dot on the precision/recall plots
        to indicate where at least 25 segments have been predicted.

        Parameters
        ----------
        min_extracted_segment_count : int
        sorted_cumulative_segment_len_bins : list of int
        predicted_segments_w_min_seg_len_count_dict : dict of { int : int }
        """
        min_extracted_segment_count_idx = -1
        for seg_len_idx, seg_len in enumerate(sorted_cumulative_segment_len_bins[::-1]):
            segment_bin_count = predicted_segments_w_min_seg_len_count_dict[seg_len]
            if segment_bin_count >= min_extracted_segment_count:
                min_extracted_segment_count_idx = (len(sorted_cumulative_segment_len_bins) - 1) - seg_len_idx
                break

        return min_extracted_segment_count_idx