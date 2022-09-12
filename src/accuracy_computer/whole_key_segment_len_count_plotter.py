""" Used to plot the number of segments with length >= len
that are predicted entirely correctly. This is done for
the clear key segments, the thresholded key segments,
and the clear thresholded key segments.
"""

from matplotlib import pyplot as plt

class WholeKeySegmentLenCountPlotter:
    """ Used to plot the segment count for each segment length.
    """

    def __init__(self, c_ks_whole_key_segment_stats_computer, t_ks_whole_key_segment_stats_computer,
                 ct_ks_whole_key_segment_stats_computer, clear_key_segment_type=None, plot_in_log_space=False):
        """

        Parameters
        ----------
        c_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        t_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        ct_ks_whole_key_segment_stats_computer : WholeKeySegmentStatsComputer
        clear_key_segment_type : str
            Key segment definition used to create the clear key segments.
        plot_in_log_space : bool
        """
        self.c_ks_segment_len_bins = c_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins
        self.c_ks_correct_whole_segments_w_min_seg_len_count = c_ks_whole_key_segment_stats_computer.sorted_correct_whole_predicted_segments_w_min_seg_len_count
        self.c_ks_predicted_segments_w_min_seg_len_count = c_ks_whole_key_segment_stats_computer.sorted_predicted_segments_w_min_seg_len_count
        self.c_ks_whole_segments_acc = self.compute_whole_segments_acc(self.c_ks_correct_whole_segments_w_min_seg_len_count, self.c_ks_predicted_segments_w_min_seg_len_count)
        self.c_ks_min_extracted_segment_count_idx = c_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        self.t_ks_segment_len_bins = t_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins
        self.t_ks_correct_whole_segments_w_min_seg_len_count = t_ks_whole_key_segment_stats_computer.sorted_correct_whole_predicted_segments_w_min_seg_len_count
        self.t_ks_predicted_segments_w_min_seg_len_count = t_ks_whole_key_segment_stats_computer.sorted_predicted_segments_w_min_seg_len_count
        self.t_ks_whole_segments_acc = self.compute_whole_segments_acc(self.t_ks_correct_whole_segments_w_min_seg_len_count, self.t_ks_predicted_segments_w_min_seg_len_count)
        self.t_ks_min_extracted_segment_count_idx = t_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        self.ct_ks_segment_len_bins = ct_ks_whole_key_segment_stats_computer.sorted_cumulative_segment_len_bins
        self.ct_ks_correct_whole_segments_w_min_seg_len_count = ct_ks_whole_key_segment_stats_computer.sorted_correct_whole_predicted_segments_w_min_seg_len_count
        self.ct_ks_predicted_segments_w_min_seg_len_count = ct_ks_whole_key_segment_stats_computer.sorted_predicted_segments_w_min_seg_len_count
        self.ct_ks_whole_segments_acc = self.compute_whole_segments_acc(self.ct_ks_correct_whole_segments_w_min_seg_len_count, self.ct_ks_predicted_segments_w_min_seg_len_count)
        self.ct_ks_min_extracted_segment_count_idx = ct_ks_whole_key_segment_stats_computer.min_extracted_segment_count_idx

        self.plot_in_log_space = plot_in_log_space

        self.X_AXIS_UPPER_LIM = 250.0

        self.clear_key_segment_type = clear_key_segment_type

    def compute_whole_segments_acc(self, correct_whole_segments_w_min_seg_len_count, predicted_segments_w_min_seg_len_count):
        """ Compute the cumulative accuracy (equivalent to the whole key segment precision*)
        for each segment length.

        *The precision is computed as follows, assuming the current segment length is len:
        (no. correctly predicted segments with length >= len) / (total no. predicted segments with length >= len)

        Parameters
        ----------
        correct_whole_segments_w_min_seg_len_count : dict of { int : int } 
        predicted_segments_w_min_seg_len_count : dict of { int : int } 
        """
        whole_segments_acc = []

        for (bin_correct_whole_segments_w_min_seg_len_count, bin_predicted_segments_w_min_seg_len_count) in zip(correct_whole_segments_w_min_seg_len_count, predicted_segments_w_min_seg_len_count):
            bin_whole_segments_acc = bin_correct_whole_segments_w_min_seg_len_count / bin_predicted_segments_w_min_seg_len_count
            whole_segments_acc.append(bin_whole_segments_acc)

        return whole_segments_acc

    def plot_seg_len_vs_correct_segments_in_log_space(self):
        """ Plot segment lengths vs. log of no. of entirely correct 
        segments for the clear key segments, thresholded key segments,
        and clear thresholded key segments.
        """
        fig, ax = plt.subplots()

        plt.xlim(0.0, self.X_AXIS_UPPER_LIM)

        strided_c_ks_correct_whole_segments_w_min_seg_len_count = [ self.c_ks_correct_whole_segments_w_min_seg_len_count[idx] for idx in range(0, len(self.c_ks_correct_whole_segments_w_min_seg_len_count), 50) ]
        strided_c_ks_segment_len_bins = [ self.c_ks_segment_len_bins[idx] for idx in range(0, len(self.c_ks_segment_len_bins), 50) ]
        strided_c_ks_whole_segments_acc = [self.c_ks_whole_segments_acc[idx] for idx in range(0, len(self.c_ks_whole_segments_acc), 50) ]

        strided_ct_ks_correct_whole_segments_w_min_seg_len_count = [ self.ct_ks_correct_whole_segments_w_min_seg_len_count[idx] for idx in range(0, len(self.ct_ks_correct_whole_segments_w_min_seg_len_count), 50) ]
        strided_ct_ks_segment_len_bins = [ self.ct_ks_segment_len_bins[idx] for idx in range(0, len(self.ct_ks_segment_len_bins), 50) ]
        strided_ct_ks_whole_segments_acc = [ self.ct_ks_whole_segments_acc[idx] for idx in range(0, len(self.ct_ks_whole_segments_acc), 50) ]

        strided_t_ks_correct_whole_segments_w_min_seg_len_count = [ self.t_ks_correct_whole_segments_w_min_seg_len_count[idx] for idx in range(0, len(self.t_ks_correct_whole_segments_w_min_seg_len_count), 50) ]
        strided_t_ks_segment_len_bins = [ self.t_ks_segment_len_bins[idx] for idx in range(0, len(self.t_ks_segment_len_bins), 50) ]
        strided_t_ks_whole_segments_acc = [ self.t_ks_whole_segments_acc[idx] for idx in range(0, len(self.t_ks_whole_segments_acc), 50) ]

        self.plot_seg_len_vs_correct_segments_in_log_space_for_ks(strided_t_ks_segment_len_bins,
                                                                  strided_t_ks_correct_whole_segments_w_min_seg_len_count,
                                                                  strided_t_ks_whole_segments_acc,
                                                                  ax, '#ff7f0e', 'T-KS',
                                                                  x_annotations_offset=1.0, y_annotations_offset=1.0)

        self.plot_seg_len_vs_correct_segments_in_log_space_for_ks(strided_c_ks_segment_len_bins,
                                                                  strided_c_ks_correct_whole_segments_w_min_seg_len_count,
                                                                  strided_c_ks_whole_segments_acc,
                                                                  ax, 'midnightblue', 'C-KS')

        self.plot_seg_len_vs_correct_segments_in_log_space_for_ks(strided_ct_ks_segment_len_bins,
                                                                  strided_ct_ks_correct_whole_segments_w_min_seg_len_count,
                                                                  strided_ct_ks_whole_segments_acc,
                                                                  ax, 'green', 'CT-KS',
                                                                  x_annotations_offset=-6.0, y_annotations_offset=-2.0)

        legend = ax.legend(loc='upper right', shadow=True, fontsize='small')

        plot_title = self.get_seg_len_vs_correct_segments_in_log_space_plot_title()
        plt.title(plot_title)
        plt.xlabel("Segment Lengths")
        plt.ylabel("Log Cumulative No. Correct Whole Segments")

        output_plot_filename = self.get_seg_len_vs_correct_segments_in_log_space_output_plot_filename()
        plt.savefig(output_plot_filename)

    def plot_seg_len_vs_correct_segments_in_log_space_for_ks(self, strided_ks_segment_len_bins,
                                                             strided_ks_correct_whole_segments_w_min_seg_len_count,
                                                             strided_ks_whole_segments_acc, ax, color, label,
                                                             x_annotations_offset=0.0, y_annotations_offset=0.0):
        """ Plot segment length vs. log of no. correct segments for one
        set of key segments (i.e. clear KS, thresholded KS, or clear
        thresholded KS).  

        Parameters
        ----------
        strided_ks_segment_len_bins : list of int
        strided_ks_correct_whole_segments_w_min_seg_len_count : list of int 
        strided_ks_whole_segments_acc : list of float 
        ax : 
        color : str
        label : str
        x_annotations_offset : float
        y_annotations_offset : float

        """
        ax.semilogy(strided_ks_segment_len_bins, strided_ks_correct_whole_segments_w_min_seg_len_count, c=color, label=label)

    def get_seg_len_vs_correct_segments_in_log_space_plot_title(self):
        """ Get the title for the segment length vs. no. correct
        segments in log space plot. 
        """
        return "Segment Len. vs. Log Cum. No. Correct Whole Segments" 

    def get_seg_len_vs_correct_segments_in_log_space_output_plot_filename(self):
        """ Get the output filename for the segment length vs. no.
        correct segments in log space plot.
        """
        return "out/plots/micchi_model2021_segment_lens_vs_log_correct_whole_segments"

    def plot_seg_len_vs_correct_segments(self):
        """ Plot segment lengths vs. no. of entirely correct 
        segments for the clear key segments, thresholded key
        segments, and clear thresholded key segments.
        """
        fig, ax = plt.subplots()

        plt.xlim(0.0, 250.0)
        #plt.ylim(0.0, 200.0)

        self.plot_seg_len_vs_correct_segments_for_ks(self.t_ks_segment_len_bins,
                                                     self.t_ks_correct_whole_segments_w_min_seg_len_count,
                                                     self.t_ks_whole_segments_acc,
                                                     self.t_ks_min_extracted_segment_count_idx,
                                                     ax, '#ff7f0e', 'T-KS',
                                                     x_annotations_offset=10,
                                                     y_annotations_offset=10)

        self.plot_seg_len_vs_correct_segments_for_ks(self.c_ks_segment_len_bins,
                                                     self.c_ks_correct_whole_segments_w_min_seg_len_count,
                                                     self.c_ks_whole_segments_acc,
                                                     self.c_ks_min_extracted_segment_count_idx,
                                                     ax, 'midnightblue', 'C-KS',
                                                     x_annotations_offset=25,
                                                     y_annotations_offset=20)

        self.plot_seg_len_vs_correct_segments_for_ks(self.ct_ks_segment_len_bins,
                                                     self.ct_ks_correct_whole_segments_w_min_seg_len_count,
                                                     self.ct_ks_whole_segments_acc,
                                                     self.ct_ks_min_extracted_segment_count_idx,
                                                     ax, 'green', 'CT-KS',
                                                     x_annotations_offset=40,
                                                     y_annotations_offset=30)

        legend = ax.legend(loc='upper right', shadow=True, fontsize='small')

        plot_title = self.get_seg_len_vs_correct_segments_plot_title()
        plt.title(plot_title)
        plt.xlabel("Segment Lengths")
        plt.ylabel("Cumulative No. Correct Whole Segments")

        output_plot_filename = self.get_seg_len_vs_correct_segments_output_plot_filename()
        plt.savefig(output_plot_filename)

    def plot_seg_len_vs_correct_segments_for_ks(self, ks_segment_len_bins, ks_correct_whole_segments_w_min_seg_len_count,
                                                ks_whole_segments_acc, ks_min_extracted_segment_count_idx, ax, color, label,
                                                x_annotations_offset=0.0, y_annotations_offset=0.0):
        """ Plot segment length vs. no. correct segments for one
        set of key segments (i.e. clear KS, thresholded KS, or clear
        thresholded KS).  

        Parameters
        ----------
        ks_segment_len_bins : list of int 
        ks_correct_whole_segments_w_min_seg_len_count : list of int 
        ks_whole_segments_acc : list of float
        ks_min_extracted_segment_count_idx : int 
            Point at which at least the minimimum number of segments
            is predicted.
        ax : 
        color : str
        label : str
        x_annotations_offset : float
        y_annotations_offset : float
        """
        ax.plot(ks_segment_len_bins, ks_correct_whole_segments_w_min_seg_len_count, c=color, label=label)
        for i in range(0, len(ks_whole_segments_acc), 50):
            at = ax.annotate(round(ks_whole_segments_acc[i], 2), (ks_segment_len_bins[i], ks_correct_whole_segments_w_min_seg_len_count[i]),
                             fontsize='small', c=color)
            at.set_x(ks_segment_len_bins[i] + x_annotations_offset)
            at.set_y(ks_correct_whole_segments_w_min_seg_len_count[i] + y_annotations_offset)
        ks_min_extracted_segment_count_x_idx = ks_segment_len_bins[ks_min_extracted_segment_count_idx]
        ks_min_extracted_segment_count_y_idx = ks_correct_whole_segments_w_min_seg_len_count[ks_min_extracted_segment_count_idx]
        ax.plot(ks_min_extracted_segment_count_x_idx, ks_min_extracted_segment_count_y_idx,'o', c=color) 

    def get_seg_len_vs_correct_segments_plot_title(self):
        """ Get the title for the segment length vs. no. correct
        segments plot. 
        """
        return "Segment Lengths vs. Cumulative No. Correct Whole Segments" 

    def get_seg_len_vs_correct_segments_output_plot_filename(self):
        """ Get the output filename for the segment length vs. no.
        correct segments plot.
        """
        if self.clear_key_segment_type is not None:
            return "out/plots/" + self.clear_key_segment_type + "_micchi_model2021_segment_lens_vs_correct_whole_segments"
        else:
            return "out/plots/micchi_model2021_segment_lens_vs_correct_whole_segments"