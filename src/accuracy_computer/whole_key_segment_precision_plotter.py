""" Used to plot the cumulative whole segment precision values
for each segment length. This is done for the clear key segments,
the thresholded key segments, and the clear thresholded key
segments.
"""

from matplotlib import pyplot as plt

class WholeKeySegmentPrecisionPlotter:
    """ Used to plot the cumulative whole segment precision values* for
    each segment length.

    *The precision is computed as follows, assuming the current segment length is len:
    (no. correctly predicted segments with length >= len) / (total no. predicted segments with length >= len)
    """

    def __init__(self, c_ks_whole_key_segment_stats_computer, t_ks_whole_key_segment_stats_computer,
                 ct_ks_whole_key_segment_stats_computer):
        """

        Parameters
        ----------
        c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        """
        self.c_ks_segment_len_bins = c_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins
        self.c_ks_whole_segment_precisions = self.compute_whole_segments_precisions(c_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins,
                                                                                    c_ks_whole_key_segment_stats_computer.correct_whole_predicted_segments_w_min_seg_len_count_dict,
                                                                                    c_ks_whole_key_segment_stats_computer.predicted_segments_w_min_seg_len_count_dict)
        self.c_ks_min_extracted_segment_count_idx = c_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        self.t_ks_segment_len_bins = t_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins
        self.t_ks_whole_segment_precisions = self.compute_whole_segments_precisions(t_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins,
                                                                                    t_ks_whole_key_segment_stats_computer.correct_whole_predicted_segments_w_min_seg_len_count_dict,
                                                                                    t_ks_whole_key_segment_stats_computer.predicted_segments_w_min_seg_len_count_dict)
        self.t_ks_min_extracted_segment_count_idx = t_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        self.ct_ks_segment_len_bins = ct_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins
        self.ct_ks_whole_segment_precisions = self.compute_whole_segments_precisions(ct_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins,
                                                                                     ct_ks_whole_key_segment_stats_computer.correct_whole_predicted_segments_w_min_seg_len_count_dict,
                                                                                     ct_ks_whole_key_segment_stats_computer.predicted_segments_w_min_seg_len_count_dict)
        self.ct_ks_min_extracted_segment_count_idx = ct_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        self.X_AXIS_UPPER_LIM = 250.0

    def compute_whole_segments_precisions(self, sorted_segment_len_bins, correct_whole_segments_count_dict,
                                          segments_count_dict):
        """ Create a dictionary where the key is the segment length and the
        value is the cumulative whole segment precision.

        Parameters
        ---------- 
        sorted_segment_len_bins: dict of {int : int}
        correct_whole_segments_count_dict: dict of {int : int}
        segments_count_dict: dict of {int : int}
        """
        whole_segments_precision_dict = {}
        for seg_len in sorted_segment_len_bins:
            if seg_len not in correct_whole_segments_count_dict:
                whole_segments_precision_dict[seg_len] = 0.0
            else:
                correct_whole_segments_count = correct_whole_segments_count_dict[seg_len]
                segment_count = segments_count_dict[seg_len]
                whole_segments_precision_dict[seg_len] = (correct_whole_segments_count / segment_count) 

        whole_segments_precisions = [ whole_segments_precision_dict[seg_len] for seg_len in sorted_segment_len_bins ]

        return whole_segments_precisions

    def plot_seg_len_vs_precision(self):
        """ Plot cumulative segment lengths vs. whole segment
        precision for the clear key segments, thresholded key
        segments, and clear thresholded key segments.
        """
        fig, ax = plt.subplots()

        plt.xlim(0.0, self.X_AXIS_UPPER_LIM)
        plt.ylim(0.0, 1.1)

        ax.plot(self.c_ks_segment_len_bins, self.c_ks_whole_segment_precisions, c='midnightblue', label="C-KS")
        ax.plot(self.t_ks_segment_len_bins, self.t_ks_whole_segment_precisions, c='#ff7f0e', label="T-KS")
        ax.plot(self.ct_ks_segment_len_bins, self.ct_ks_whole_segment_precisions, c='green', label="CT-KS")

        c_ks_min_extracted_segment_count_x_idx = self.c_ks_segment_len_bins[self.c_ks_min_extracted_segment_count_idx]
        c_ks_min_extracted_segment_count_y_idx = self.c_ks_whole_segment_precisions[self.c_ks_min_extracted_segment_count_idx]
        print("C-KS cutoff: idx: {} ({}, {})".format(self.c_ks_min_extracted_segment_count_idx,
                                                     c_ks_min_extracted_segment_count_x_idx,
                                                     c_ks_min_extracted_segment_count_y_idx))
        ax.plot(c_ks_min_extracted_segment_count_x_idx, c_ks_min_extracted_segment_count_y_idx, 'o',
                c='midnightblue') 

        t_ks_min_extracted_segment_count_x_idx = self.t_ks_segment_len_bins[self.t_ks_min_extracted_segment_count_idx]
        t_ks_min_extracted_segment_count_y_idx = self.t_ks_whole_segment_precisions[self.t_ks_min_extracted_segment_count_idx]
        print("T-KS cutoff: idx: {} ({}, {})".format(self.t_ks_min_extracted_segment_count_idx,
                                                     t_ks_min_extracted_segment_count_x_idx,
                                                     t_ks_min_extracted_segment_count_y_idx))
        ax.plot(t_ks_min_extracted_segment_count_x_idx, t_ks_min_extracted_segment_count_y_idx, 'o',
                c='#ff7f0e') 

        ct_ks_min_extracted_segment_count_x_idx = self.ct_ks_segment_len_bins[self.ct_ks_min_extracted_segment_count_idx]
        ct_ks_min_extracted_segment_count_y_idx = self.ct_ks_whole_segment_precisions[self.ct_ks_min_extracted_segment_count_idx]
        print("CT-KS cutoff: idx: {} ({}, {})".format(self.ct_ks_min_extracted_segment_count_idx,
                                                      ct_ks_min_extracted_segment_count_x_idx,
                                                      ct_ks_min_extracted_segment_count_y_idx))
        ax.plot(ct_ks_min_extracted_segment_count_x_idx, ct_ks_min_extracted_segment_count_y_idx, 'o',
                c='green') 

        legend = ax.legend(loc='upper right', shadow=True, fontsize='small')

        plot_title = self.get_seg_len_vs_precision_plot_title()
        plt.title(plot_title)
        plt.xlabel("Segment Lengths")
        plt.ylabel("Precision")

        output_plot_filename = self.get_seg_len_vs_precision_plot_filename()
        plt.savefig(output_plot_filename)

    def get_seg_len_vs_precision_plot_title(self):
        """ Get segment length vs. precision plot title.
        """
        return "Segment Len. vs. Precision" 

    def get_seg_len_vs_precision_plot_filename(self):
        """ Get segment length vs. precision plot filename.
        """
        return "out/plots/micchi_model2021_segment_lens_vs_precision"