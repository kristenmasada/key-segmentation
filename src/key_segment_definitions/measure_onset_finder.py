"""
"""

class MeasureOnsetFinder:
    """
    """

    def __init__(self, parsed_mxl):
        """
        """
        self.parsed_mxl_starts_on_measure_zero = False
        self.measure_nums_to_measure_onsets = self.get_measure_nums_to_measure_onsets(parsed_mxl)
        self.total_num_measures = len(self.measure_nums_to_measure_onsets)
        self.last_measure_num = max(self.measure_nums_to_measure_onsets) 

    def get_measure_nums_to_measure_onsets(self, parsed_mxl):
        """

        Parameters
        ----------
        parsed_mxl : music21.stream.Score

        Returns
        -------
        measure_nums_to_measure_onsets : dict {int : float}

        Notes
        -----
        *This code is a modified version of the `AnnotationConverter._get_measure_offsets()`
         method from frog.
        - `measures_list[0]` because there might be more than one part (e.g. piano
          right and left hand, other instruments, etc.).
        - Check if `first_part_measure.numberSuffix is None` because consider only
          measures that have not been marked as "excluded" in the musicxml (for example
          using Musescore).
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