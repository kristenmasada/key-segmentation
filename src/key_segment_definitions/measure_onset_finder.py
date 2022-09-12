""" Find the number and onset time of each measure in a song.
"""

class MeasureOnsetFinder:
    """ Find the number and onset time of each measure in a song.
    """

    def __init__(self, parsed_mxl):
        """

        Parameters
        ----------
        parsed_mxl : music21.stream.Score
        """
        self.parsed_mxl_starts_on_measure_zero = False
        self.measure_nums_to_measure_onsets = self.get_measure_nums_to_measure_onsets(parsed_mxl)
        self.total_num_measures = len(self.measure_nums_to_measure_onsets)
        self.last_measure_num = max(self.measure_nums_to_measure_onsets) 

    def get_measure_nums_to_measure_onsets(self, parsed_mxl):
        """ From the parsed MusicXML, create a dictionary that maps the
        number of each measure to the onset time of that measure.
        
        There are instances where the first measure in a song has
        number 0 instead of 1. If this is the case, shift all of
        the measure numbers by 1 to ensure the first measure has
        measure number 1.

        Parameters
        ----------
        parsed_mxl : music21.stream.Score

        Returns
        -------
        measure_nums_to_measure_onsets : dict {int : float}

        Notes
        -----
        *This function is a modified version of the `AnnotationConverter._get_measure_offsets()`
         method from Micchi, et al.'s frog code.
        - On line 51, `measures_list[0]` is used because there might be more than one part
          (e.g. piano right and left hand, other instruments, etc.).
        - On line 52, check if `first_part_measure.numberSuffix is None` because only
          measures that have not been marked as "excluded" in the MusicXML should be
          considered.
        """
        measure_onset_map = parsed_mxl.measureOffsetMap()

        measure_nums_to_measure_onsets = {}
        for measure_onset, measures_list in measure_onset_map.items():
            first_part_measure = measures_list[0]
            if first_part_measure.numberSuffix is None:
                measure_nums_to_measure_onsets[first_part_measure.number] = measure_onset 
            else:
                print("Warning: measure {} excluded.".format(first_part_measure.number))

        if min(measure_nums_to_measure_onsets) == 0:
            self.parsed_mxl_starts_on_measure_zero = True
            measure_nums_to_measure_onsets = { (measure_num + 1): measure_nums_to_measure_onsets[measure_num] for measure_num in measure_nums_to_measure_onsets }

        try:
            assert min(measure_nums_to_measure_onsets) == 1
        except:
            raise Exception("Minimum measure number is 0 instead of 1.")

        return measure_nums_to_measure_onsets