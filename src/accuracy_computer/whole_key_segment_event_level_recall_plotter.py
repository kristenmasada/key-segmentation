""" Used to plot the cumulative whole segment event-level recall
values for each segment length. This is done for the clear key
segments, the thresholded key segments, and the clear thresholded key
segments.
"""

from matplotlib import pyplot as plt

class WholeKeySegmentEventLevelRecallPlotter:
    """ Used to plot the cumulative whole segment event-level recall
    values* for each segment length.

    *The event-level recall is computed as follows, assuming the current
    segment length is len:
    (total no. events in correctly predicted segments with length >= len) / 
    (total no. events in the ground truth segments with length >= len)

    *The option to alternatively compute the event-level recall as follows is provided
    as well:
    (total no. events in correctly predicted segments with length >= len) / (total no. events in song)
    """

    def __init__(self, clear_key_definition, c_ks_whole_key_segment_stats_computer,
                 t_ks_whole_key_segment_stats_computer, ct_ks_whole_key_segment_stats_computer,
                 use_total_num_events_as_divisor=True):
        """

        Parameters
        ----------
        clear_key_definition : str
        c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        use_total_num_events_as_divisor : bool
            If true, to compute the event-level recall values, divide by (total no. events
            in song) instead of (total no. events in the ground truth segments with length ≥ len).
        """
        self.clear_key_definition = clear_key_definition

        self.c_ks_segment_len_bins = sorted(list(c_ks_whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_event_count_dict.keys()))
        self.c_ks_whole_segment_event_level_recalls = self.get_segment_event_level_recalls_stats(c_ks_whole_key_segment_stats_computer, use_total_num_events_as_divisor)
        self.c_ks_min_extracted_segment_count_idx = c_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        #print("C-KS correct seg. count dict.:", c_ks_whole_key_segment_stats_computer.correct_whole_predicted_segments_w_min_seg_len_event_count_dict)

        self.t_ks_segment_len_bins = sorted(list(t_ks_whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_event_count_dict.keys()))
        self.t_ks_whole_segment_event_level_recalls = self.get_segment_event_level_recalls_stats(t_ks_whole_key_segment_stats_computer, use_total_num_events_as_divisor)
        self.t_ks_min_extracted_segment_count_idx = t_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        self.ct_ks_segment_len_bins = sorted(list(ct_ks_whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_event_count_dict.keys()))
        self.ct_ks_whole_segment_event_level_recalls = self.get_segment_event_level_recalls_stats(ct_ks_whole_key_segment_stats_computer, use_total_num_events_as_divisor)
        self.ct_ks_min_extracted_segment_count_idx = ct_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        #self.compare_c_ks_and_t_ks_stats(c_ks_whole_key_segment_stats_computer, t_ks_whole_key_segment_stats_computer)

        self.X_AXIS_UPPER_LIM = 250.0

    def get_segment_event_level_recalls_stats(self, whole_key_segment_stats_computer, use_total_num_events_as_divisor=False):
        """ Get the segment lengths and the cumulative whole segment
        event-level recall values for each of these segment lengths.

        Parameters
        ----------
        whole_key_segment_stats_computer : WholeKeySegmentStatsComputer 
        use_total_num_events_as_divisor : bool
        """
        if use_total_num_events_as_divisor:
            whole_segments_recall_dict = self.compute_whole_segments_recall_dict(whole_key_segment_stats_computer.correct_whole_predicted_segments_w_min_seg_len_event_count_dict,
                                                                                 whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_event_count_dict,
                                                                                 total_num_events=whole_key_segment_stats_computer.total_num_events)
        else:
            whole_segments_recall_dict = self.compute_whole_segments_recall_dict(whole_key_segment_stats_computer.correct_whole_predicted_segments_w_min_seg_len_event_count_dict,
                                                                                 whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_event_count_dict)

        segment_lens = [ segment_len for segment_len in sorted(list(whole_segments_recall_dict.keys())) ]
        whole_segment_event_level_recalls = [ whole_segments_recall_dict[segment_len] for segment_len in segment_lens ]

        return whole_segment_event_level_recalls

    def compute_whole_segments_recall_dict(self, correct_whole_segments_event_count_dict,
                                           ground_truth_segments_event_count_dict,
                                           total_num_events=None):
        """ Create a dictionary where the key is the segment length
        and the value is the cumulative whole segment event-level recall.

        Parameters
        ---------- 
        correct_whole_segments_event_count_dict : dict of {int : int}
        ground_truth_segments_event_count_dict : dict of {int : int}
        total_num_events : int
        """
        whole_segments_recall_dict = {}
        for seg_len in ground_truth_segments_event_count_dict:
            if seg_len in correct_whole_segments_event_count_dict:
                correct_whole_segments_event_count = correct_whole_segments_event_count_dict[seg_len]
            else:
                correct_whole_segments_event_count = 0

            if total_num_events:
                whole_segments_recall_dict[seg_len] = (correct_whole_segments_event_count / total_num_events) 
            elif ground_truth_segments_event_count_dict:
                ground_truth_segments_event_count = ground_truth_segments_event_count_dict[seg_len]
                whole_segments_recall_dict[seg_len] = (correct_whole_segments_event_count / ground_truth_segments_event_count) 

        return whole_segments_recall_dict

    def plot_seg_len_vs_event_level_recall(self):
        """ Plot cumulative segment lengths vs. whole segment
        event-level recall values for the clear key segments,
        thresholded key segments, and clear thresholded key
        segments.
        """
        fig, ax = plt.subplots()

        plt.xlim(0.0, self.X_AXIS_UPPER_LIM)
        plt.ylim(0.0, 1.1)

        ax.plot(self.c_ks_segment_len_bins, self.c_ks_whole_segment_event_level_recalls, c='midnightblue', label="C-KS")
        ax.plot(self.t_ks_segment_len_bins, self.t_ks_whole_segment_event_level_recalls, c='#ff7f0e', label="T-KS")
        ax.plot(self.ct_ks_segment_len_bins, self.ct_ks_whole_segment_event_level_recalls, c='green', label="CT-KS")

        legend = ax.legend(loc='upper right', shadow=True, fontsize='small')

        c_ks_min_extracted_segment_count_x_idx = self.c_ks_segment_len_bins[self.c_ks_min_extracted_segment_count_idx]
        c_ks_min_extracted_segment_count_y_idx = self.c_ks_whole_segment_event_level_recalls[self.c_ks_min_extracted_segment_count_idx]
        ax.plot(c_ks_min_extracted_segment_count_x_idx, c_ks_min_extracted_segment_count_y_idx,'o',
                c='midnightblue') 

        t_ks_min_extracted_segment_count_x_idx = self.t_ks_segment_len_bins[self.t_ks_min_extracted_segment_count_idx]
        t_ks_min_extracted_segment_count_y_idx = self.t_ks_whole_segment_event_level_recalls[self.t_ks_min_extracted_segment_count_idx]
        ax.plot(t_ks_min_extracted_segment_count_x_idx, t_ks_min_extracted_segment_count_y_idx,'o',
                c='#ff7f0e') 

        ct_ks_min_extracted_segment_count_x_idx = self.ct_ks_segment_len_bins[self.ct_ks_min_extracted_segment_count_idx]
        ct_ks_min_extracted_segment_count_y_idx = self.ct_ks_whole_segment_event_level_recalls[self.ct_ks_min_extracted_segment_count_idx]
        ax.plot(ct_ks_min_extracted_segment_count_x_idx, ct_ks_min_extracted_segment_count_y_idx,'o',
                c='green') 

        plot_title = self.get_seg_len_vs_event_level_recall_plot_title()
        plt.title(plot_title)
        plt.xlabel("Segment Lengths")
        plt.ylabel("Event-Level Recall")

        output_plot_filename = self.get_seg_len_vs_event_level_recall_plot_filename()
        plt.savefig(output_plot_filename)

    def get_seg_len_vs_event_level_recall_plot_title(self):
        """ Get segment length vs. event-level recall plot title.
        """
        return "Segment Len. vs. Event-Level Recall ({})".format(self.clear_key_definition)

    def get_seg_len_vs_event_level_recall_plot_filename(self):
        """ Get segment length vs. event-level recall plot filename.
        """
        return "out/plots/meta-corpus_validation_event_level_recall_plot_" + self.clear_key_definition