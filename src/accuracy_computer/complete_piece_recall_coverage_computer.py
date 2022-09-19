""" Compute and output the complete piece recall and
coverage over all of the songs.
"""

class CompletePieceRecallCoverageComputer:
    """ Compute and output the complete piece recall and
    coverage over all of the songs.
    """

    def __init__(self, num_correctly_predicted_events, num_events_in_predicted_segments,
                 ground_truth_key_labels_dict):
        """

        Parameters
        ----------
        num_correctly_predicted_events : int
            No. events where the key was predicted correctly over all of the songs. 
        num_events_in_predicted_segments : int
            Total no. events in the predicted segments over all of the songs.
        ground_truth_key_labels_dict : dict of { str : np.ndarray }
            Used to predict the total number of events over all of the songs.
        """
        self.num_correctly_predicted_events = num_correctly_predicted_events
        self.num_events_in_predicted_segments = num_events_in_predicted_segments
        self.total_num_events = self.compute_total_num_events(ground_truth_key_labels_dict)

    def compute_total_num_events(self, ground_truth_key_labels_dict):
        """ Compute the total number of events over all of the
        songs.

        Parameters
        ----------
        ground_truth_key_labels_dict : dict of { str : np.ndarray }
        """
        total_num_events = 0
        for songname in ground_truth_key_labels_dict:
            total_num_events += ground_truth_key_labels_dict[songname].shape[0]

        return total_num_events

    def compute_and_output_recall_and_coverage(self):
        """ Compute and output the complete piece recall and
        coverage over all of the songs.
        """
        recall = (self.num_correctly_predicted_events / self.total_num_events) * 100.0
        print("Recall: {:.1f}% ({}/{})".format(recall, self.num_correctly_predicted_events,
                                               self.total_num_events))

        coverage = (self.num_events_in_predicted_segments / self.total_num_events) * 100.0
        print("Coverage: {:.1f}% ({}/{})".format(coverage, self.num_events_in_predicted_segments,
                                                 self.total_num_events))