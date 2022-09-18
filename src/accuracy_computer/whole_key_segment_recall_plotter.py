""" Used to plot the cumulative whole segment recall values for
each segment length. This is done for the clear key segments,
the thresholded key segments, and the clear thresholded key
segments.
"""

from matplotlib import pyplot as plt

class WholeKeySegmentRecallPlotter:
    """ Used to plot the cumulative whole segment recall values* for
    each segment length.

    *The recall is computed as follows, assuming the current segment length is len:
    (no. correctly predicted segments with length >= len) / (no. ground truth segments with length >= len) 
    """

    def __init__(self, clear_key_definition, c_ks_whole_key_segment_stats_computer, t_ks_whole_key_segment_stats_computer,
                 ct_ks_whole_key_segment_stats_computer):
        """

        Parameters
        ----------
        clear_key_definition : str
        c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        """
        self.clear_key_definition = clear_key_definition
        self.c_ks_segment_len_bins = sorted(list(c_ks_whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_event_count_dict.keys()))
        self.c_ks_whole_segment_recalls = self.get_segment_recall_stats(c_ks_whole_key_segment_stats_computer)

        self.t_ks_segment_len_bins = sorted(list(t_ks_whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_event_count_dict.keys()))
        self.t_ks_whole_segment_recalls = self.get_segment_recall_stats(t_ks_whole_key_segment_stats_computer)

        self.ct_ks_segment_len_bins = sorted(list(ct_ks_whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_event_count_dict.keys()))
        self.ct_ks_whole_segment_recalls = self.get_segment_recall_stats(ct_ks_whole_key_segment_stats_computer)

        self.X_AXIS_UPPER_LIM = 250.0

    def get_segment_recall_stats(self, whole_key_segment_stats_computer):
        """ Get the segment lengths and the cumulative whole segment
        recall values for each of these segment lengths.

        Parameters
        ----------
        whole_key_segment_stats_computer : WholeKeySegmentStatsComputer 
        """
        whole_segments_recall_dict = self.compute_whole_segments_recall_dict(whole_key_segment_stats_computer.correct_whole_predicted_segments_w_min_seg_len_count_dict,
                                                                             whole_key_segment_stats_computer.ground_truth_segments_w_min_seg_len_count_dict)

        segment_lens = [ segment_len for segment_len in sorted(list(whole_segments_recall_dict.keys())) ]
        whole_segment_recalls = [ whole_segments_recall_dict[segment_len] for segment_len in segment_lens ]

        return whole_segment_recalls

    def compute_whole_segments_recall_dict(self, correct_whole_segments_count_dict,
                                           ground_truth_segments_count_dict):
        """ Create a dictionary where the key is the segment length and the
        value is the cumulative whole segment recall.

        Parameters
        ---------- 
        correct_whole_segments_count_dict : dict of {int : int}
        ground_truth_segments_count_dict : dict of {int : int}
        total_num_events : int
        """
        whole_segments_recall_dict = {}
        for seg_len in ground_truth_segments_count_dict:
            if seg_len in correct_whole_segments_count_dict:
                correct_whole_segments_count = correct_whole_segments_count_dict[seg_len]
            else:
                correct_whole_segments_count = 0

            ground_truth_segments_count = ground_truth_segments_count_dict[seg_len]
            whole_segments_recall_dict[seg_len] = (correct_whole_segments_count / ground_truth_segments_count) 

        return whole_segments_recall_dict

    def plot_seg_len_vs_recall(self):
        """ Plot cumulative segment lengths vs. whole segment recall
        values for the clear key segments, thresholded key segments,
        and clear thresholded key segments.
        """
        fig, ax = plt.subplots()

        plt.xlim(0.0, self.X_AXIS_UPPER_LIM)
        plt.ylim(0.0, 1.1)

        ax.plot(self.c_ks_segment_len_bins, self.c_ks_whole_segment_recalls, c='midnightblue', label="C-KS")
        ax.plot(self.t_ks_segment_len_bins, self.t_ks_whole_segment_recalls, c='#ff7f0e', label="T-KS")
        ax.plot(self.ct_ks_segment_len_bins, self.ct_ks_whole_segment_recalls, c='green', label="CT-KS")

        legend = ax.legend(loc='upper right', shadow=True, fontsize='small')

        plot_title = self.get_seg_len_vs_recall_plot_title()
        plt.title(plot_title)
        plt.xlabel("Segment Lengths")
        plt.ylabel("Recall")

        output_plot_filename = self.get_seg_len_vs_recall_plot_filename()
        plt.savefig(output_plot_filename)

    def get_seg_len_vs_recall_plot_title(self):
        """ Get segment length vs. recall plot title.
        """
        return "Segment Len. vs. Recall ({})".format(self.clear_key_definition)

    def get_seg_len_vs_recall_plot_filename(self):
        """ Get segment length vs. recall plot filename.
        """
        return "out/plots/meta-corpus_validation_recall_plot_" + self.clear_key_definition