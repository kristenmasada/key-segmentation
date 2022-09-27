""" Used to compute the average segment length over all of the
songs in the dataset. Can also compute the frequency of
occurrence of segments of each length.
"""

from matplotlib import pyplot as plt
import numpy as np

from utils import compute_key_segment_length

class FragmentationComputer:
    """ Used to compute the average segment length over all of the
    songs in the dataset. Can also compute the frequency of
    occurrence of segments of each length.
    """

    def __init__(self, key_segments_dict, threshold=-1.0):
        """

        Parameters
        ----------
        key_segments_dict : dict of {str : [int, int]}
            Two ints specify the eighth note beat start time and end
            time of each key segment.
        threshold : float
            Threshold value used to generate the key segments provided
            in `key_segments_dict`.
            If the value passed in is -1.0, this means that no threshold
            was used to generate the key segments.
            *I just output the threshold value. The threshold doesn't have
            any impact on the fragmentation computations.
        """
        self.key_segments_dict = key_segments_dict

        self.threshold = threshold

    def compute_and_output_avg_segment_len(self):
        """ Compute and output the average segment length over
        all songs.
        """
        avg_segment_len, total_num_segment_events, num_segments = self.compute_avg_segment_len()

        if self.threshold == -1.0:
            print("Avg. segment length: {:.2f} ({} total no. segment events / {} no. segments)".format(
                                                                                        avg_segment_len,
                                                                                        total_num_segment_events,
                                                                                        num_segments))
        else:
            print("Avg. segment length (threshold: {:.3f}): {:.2f} ({} total no. segment events / {} no. segments)".format(
                                                                                        self.threshold,
                                                                                        avg_segment_len,
                                                                                        total_num_segment_events,
                                                                                        num_segments))

    def compute_avg_segment_len(self):
        """ Compute the average segment length over all songs.
        Computed as (total number of events over all of the
        segments) / (total number of segments).
        """
        total_num_segment_events = 0
        total_num_segments = 0

        for songname in self.key_segments_dict:
            song_key_segments = self.key_segments_dict[songname]
            num_segment_events = sum([compute_key_segment_length(key_segment) for key_segment in song_key_segments])
            total_num_segment_events += num_segment_events
            num_key_segments = len(song_key_segments)
            total_num_segments += num_key_segments

        avg_segment_len = total_num_segment_events / total_num_segments
        return avg_segment_len, total_num_segment_events, total_num_segments

    def compute_segment_length_to_frequency_dict(self):
        """ Create a dictionary where the keys are all of the
        key segment lengths that appear over all of the songs
        and the values are counts of how many segments with
        that length exist in the dataset.
        """
        segment_length_to_frequency_dict = {}

        for songname in self.key_segments_dict:
            song_key_segments = self.key_segments_dict[songname]

            for key_segment in song_key_segments:
                key_segment_length = compute_key_segment_length(key_segment)
                if key_segment_length in segment_length_to_frequency_dict:
                    segment_length_to_frequency_dict[key_segment_length] += 1
                else:
                    segment_length_to_frequency_dict[key_segment_length] = 1

        return segment_length_to_frequency_dict

class SegmentLengthToFrequencyPlotter:
    """ Extra class that can be used to plot the segment length vs. the
    frequency count of each segment length if I want.
    """

    def __init__(self, segment_length_to_frequency_dict, threshold):
        """

        Parameters
        ----------
        segment_length_to_frequency_dict : { int : int }
        threshold : float
        """
        self.segment_length_to_frequency_dict = segment_length_to_frequency_dict

        self.max_segment_length = max(self.segment_length_to_frequency_dict)
        self.segment_lengths = list(segment_length_to_frequency_dict.keys())
        self.segment_length_frequencies = list(self.segment_length_to_frequency_dict.values())

        self.max_segment_frequency = max(self.segment_length_frequencies)

        self.threshold = threshold

    def plot_segment_length_to_frequency_scatter(self):
        """ Plot segment lengths vs. frequencies of each segment length
        as a scatter plot.
        """
        fig, ax = plt.subplots()

        ax.scatter(self.segment_lengths, self.segment_length_frequencies)

        plot_title = self.get_plot_title()
        plt.title(plot_title)
        plt.xlabel("Segment lengths")
        plt.ylabel("Segment length frequencies")

        plt.ylim(0, self.max_segment_frequency + 10)

        output_plot_filename = self.get_output_plot_filename()
        plt.savefig(output_plot_filename)

    def plot_segment_length_to_frequency_stem(self):
        """ Plot segment lengths vs. frequencies of each segment length
        as a stem plot.
        """
        fig, ax = plt.subplots()

        ax.stem(self.segment_lengths, self.segment_length_frequencies)

        plot_title = self.get_plot_title()
        plt.title(plot_title)
        plt.xlabel("Segment lengths")
        plt.ylabel("Segment length frequencies")

        plt.ylim(0, self.max_segment_frequency + 10)

        output_plot_filename = self.get_output_plot_filename()
        plt.savefig(output_plot_filename)

    def plot_segment_length_to_frequency_histogram(self):
        """ Plot segment lengths vs. frequencies of each segment length
        as a histogram.
        """
        fig, ax = plt.subplots()

        segment_length_bins = self.get_segment_length_bins()
        segment_length_frequency_for_each_bin = self.get_segment_length_frequency_for_each_bin(segment_length_bins)

        ax.hist(segment_length_frequency_for_each_bin, segment_length_bins)

        plot_title = self.get_plot_title()
        plt.title(plot_title)
        plt.xlabel("Segment lengths")
        plt.ylabel("Segment length frequencies")

        plt.ylim(0, self.max_segment_frequency + 10)

        output_plot_filename = self.get_output_plot_filename()
        plt.savefig(output_plot_filename)

    def get_segment_length_bins(self):
        """ Get list of segment lengths from 1, 2, ..., up to the maximum
        segment length.
        """
        return list(np.arange(1, self.max_segment_length + 2))

    def get_segment_length_frequency_for_each_bin(self, segment_length_bins):
        """ Get frequency of each segment length. Specify '0' as count
        for segment lengths that don't appear in the original
        `self.segment_length_to_frequency_dict` dictionary.

        Parameters
        ----------
        segment_length_bins : list of int
        """
        segment_length_frequency_for_each_bin = []
        for length in segment_length_bins:
            if length in self.segment_length_to_frequency_dict:
                segment_length_frequency_for_each_bin.append(self.segment_length_to_frequency_dict[length])
            else:
                segment_length_frequency_for_each_bin.append(0)

        return segment_length_frequency_for_each_bin

    def get_plot_title(self):
        """ Get plot title.
        """
        return "Segment Length Frequencies for Threshold {}".format(self.threshold)

    def get_output_plot_filename(self):
        """ Get output plot filename.
        """
        return "out/plots/micchi_model2021_threshold_{}_segment_lengths_vs_frequencies".format(int(self.threshold * 1000.0))