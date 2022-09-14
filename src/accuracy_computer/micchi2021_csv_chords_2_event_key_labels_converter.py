""" From Micchi's CSV files from the Meta-Corpus,
get the key label for each event in each song and
figure out which events in each song occur inside
a tonicization segment.
"""

from argparse import ArgumentParser
from collections import namedtuple
import csv
import math

import numpy as np

from file_handlers import NpzFileHandler
from label_codec import LabelCodec
from utils import get_filepaths_from_txt_file, \
                  strip_filename_from_filepath

# Taken from line 11 of preprocess_chords.py from frog:
Chord = namedtuple("Chord", ["key", "degree", "quality", "inversion", "root"])

# Mapping from key labels to key indices.
pitch_bass_key_indices = {'C': 0,
                          'C#': 1,
                          'D-': 1,
                          'D': 2,
                          'D#': 3,
                          'E-': 3,
                          'E': 4,
                          'F-': 4,
                          'F': 5,
                          'F#': 6,
                          'G-': 6,
                          'G': 7,
                          'G#': 8,
                          'A-': 8,
                          'A': 9,
                          'A#': 10,
                          'B-': 10,
                          'B': 11,
                          'C-': 11,
                          'c': 12,
                          'c#': 13,
                          'd-': 13,
                          'd': 14,
                          'd#': 15,
                          'e-': 15,
                          'e': 16,
                          'f': 17,
                          'f#': 18,
                          'g-': 18,
                          'g': 19,
                          'g#': 20,
                          'a-': 20,
                          'a': 21,
                          'a#': 22,
                          'b-': 22,
                          'b': 23,
                          'c-': 23 
                         }

TONICIZATION_PRESENT = 1
NO_TONICIZATION_PRESENT = 0

class Micchi2021CSVChords2EventKeyLabelsConverter:
    """ From Micchi's CSV files from the Meta-Corpus,
    get the key label for each event in each song and
    figure out which events in each song occur inside
    a tonicization segment.
    """

    def __init__(self, txt_file_with_csv_filepaths, input_type):
        """
        
        Parameters
        ----------
        txt_file_with_csv_filepaths : str
        input_type : str
        """
        self.csv_filepaths = get_filepaths_from_txt_file(txt_file_with_csv_filepaths)
        self.input_type = input_type
        self.spelling = self.input_type.split("_")[0]

    def get_event_key_labels_from_csv_files_for_all_songs(self):
        """ Create two dictionaries: one that maps each song to
        the key label for each event in the song and another that
        maps each song to a list indicating which events occur inside
        a tonicization.
        """
        label_codec = LabelCodec(spelling=self.spelling == "spelling",
                                 mode='legacy', strict=False)

        songs_to_event_key_labels = {}
        songs_to_event_tonicization_labels = {}
        for csv_filepath in self.csv_filepaths:
            song_event_chord_labels = self.import_chords(csv_filepath, label_codec)

            songname = strip_filename_from_filepath(csv_filepath)
            print("Song:", songname)

            song_event_key_labels = self.extract_keys_from_event_chord_labels(song_event_chord_labels)
            songs_to_event_key_labels[songname] = song_event_key_labels 

            song_event_tonicization_labels = self.extract_tonicizations_from_event_chord_labels(song_event_chord_labels)
            songs_to_event_tonicization_labels[songname] = song_event_tonicization_labels

        return songs_to_event_key_labels, songs_to_event_tonicization_labels

    def import_chords(self, chords_csv_file, label_codec):
        """ Get chord label for each event in the song.

        Parameters
        ----------
        chords_csv_file : str
        label_codec : LabelCodec

        Notes
        -----
        Taken from `_segment_chord_labels` function on line 97 of
        preprocess_chords.py from frog.
        """
        chord_labels = self._load_chord_labels(chords_csv_file, label_codec)
        score_length = chord_labels[-1][1]
        cl_segmented = self._segment_chord_labels(chord_labels, score_length)
        return cl_segmented

    def _load_chord_labels(self, chords_csv_file, label_codec):
        """ Load the chord labels from the CSV file.

        Parameters
        ----------
        chords_csv_file : str
            The path to the file with the harmonic analysis.
        label_codec : LabelCodec

        Notes
        -----
        Taken from line 103 of preprocess_chords.py from frog.
        """
        with open(chords_csv_file, mode="r") as f:
            data = csv.reader(f)
            # The data columns are these: start, end, key, degree, quality, inversion
            chords = [
                (
                    float(row[0]),
                    float(row[1]),
                    Chord(*row[2:], label_codec.find_chord_root_str(row[2], row[3])),
                )
                for row in data
            ]
        return chords

    def _segment_chord_labels(self, chord_labels, score_duration, output_fpc=2):
        """ Get chord label for each event in the song.

        Parameters
        ----------
        chord_labels : list of (float, float, Chord)
        score_duration : float
        output_fpc : int
            fpc = "frames per crotchet (i.e. quarter note)." An event in the Micchi
            output is an eighth note, so `output_fpc` should be 2.

        Notes
        -----
        Taken from `_segment_chord_labels` function on line 97 of
        preprocess_chords.py.
        """
        labels = []
        n_frames_to_backfill = 0
        for n in range(math.ceil(score_duration * output_fpc)):
            seg_time = n / output_fpc
            chords_found = [c[2] for c in chord_labels if c[0] <= seg_time < c[1]]
            if len(chords_found) == 0:
                print(f"Warning: Cannot read labels at frame {n}, time {seg_time}.")
                if labels:
                    chords_found = [labels[-1]]
                    print(f"Warning: Assuming that the previous chord is still valid: {chords_found}")
                else:
                    n_frames_to_backfill += 1
                    print(f"Warning: No valid chord found yet. Back-filling with the next one")
                    continue

            if len(chords_found) > 1:
                print(
                    f"Warning: More than one chord at frame {n} starting at crotchet {seg_time}:\n"
                    f"{[l for l in chords_found]}. Using only the first one."
                )
            for _ in range(1 + n_frames_to_backfill):
                labels.append(chords_found[0])
            n_frames_to_backfill = 0
        return labels

    def extract_keys_from_event_chord_labels(self, event_chord_labels):
        """ Create a numpy vector with length equal to the no. of
        events in the song. Each element has a value in the range
        0-23, indicating the key occurring at that event (see
        `pitch_bass_key_indices` for mapping from key names to
        key indices).

        Parameters
        ----------
        event_chord_labels : list of Chord 
        """
        event_keys = []
        for event_chord_label in event_chord_labels:
            key_idx = self.convert_key_str_to_key_idx(event_chord_label.key)
            event_keys.append(key_idx)

        return np.asarray(event_keys, dtype='int64')

    def convert_key_str_to_key_idx(self, key_label):
        """ Convert key label from a string to an int
        using the `pitch_bass_key_indices` dict.

        Parameters
        ----------
        key_label : str
        """
        if self.input_type == 'pitch_bass':
            return pitch_bass_key_indices[key_label] 
        else:
            raise Exception("Only `input_type` implemented so far is 'pitch_bass'.")

    def extract_tonicizations_from_event_chord_labels(self, event_chord_labels):
        """ Create a numpy vector with length equal to the no. of events
        in the song. Each element has value 0 or 1, 0 indicating that
        a tonicization does not occur at that event and 1 indicating
        that there is a tonicization occurring at that event. 

        Parameters
        ----------
        event_chord_labels : list of Chord 
        """
        event_tonicizations = []
        for event_chord_label in event_chord_labels:
            if '/' in event_chord_label.degree:
                tonicization_idx = TONICIZATION_PRESENT
            else:
                tonicization_idx = NO_TONICIZATION_PRESENT
            event_tonicizations.append(tonicization_idx)

        return np.asarray(event_tonicizations, dtype='int64')

def get_commandline_args():
    """ Get commandline argument values from user.
    """
    parser = ArgumentParser(description='From Micchi\'s CSV files from the Meta-Corpus, '
                                        'get the key label for each event in each song and '
                                        'figure out which events in each song occur inside '
                                        'a tonicization segment.')
    parser.add_argument('--txt_file_with_csv_filepaths', type=str,
                        help='Path to .txt file containing the paths to the '
                             '.csv files with the key labels for each song.')
    parser.add_argument('--input_type', type=str, choices=['pitch_bass'],
                        default='pitch_bass')
    commandline_args = parser.parse_args()

    return commandline_args

if __name__ == '__main__':
    args = get_commandline_args()

    csv_chords2event_key_labels_converter = Micchi2021CSVChords2EventKeyLabelsConverter(args.txt_file_with_csv_filepaths,
                                                                                        args.input_type)
    songs_to_event_key_labels, \
    songs_to_event_tonicization_labels = csv_chords2event_key_labels_converter.get_event_key_labels_from_csv_files_for_all_songs()

    npz_file_handler = NpzFileHandler()
    npz_file_handler.write_content_to_npz_file(songs_to_event_key_labels,
                                               'out/micchi2021_validation_event_key_gt_labels.npz')
    npz_file_handler.write_content_to_npz_file(songs_to_event_tonicization_labels,
                                               'out/micchi2021_validation_event_tonicization_gt_labels.npz')