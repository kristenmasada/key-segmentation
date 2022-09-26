from cProfile import label
import csv
import logging
import math
from collections import namedtuple
from tkinter import CHORD

from frog import NOTES, PITCH_FIFTHS, N2I, find_enharmonic_equivalent, PF2I
from frog.label_codec import KEY_START, KEY_END

logger = logging.getLogger(__name__)

Chord = namedtuple("Chord", ["key", "degree", "quality", "inversion", "root"])

ONSET_IDX, OFFSET_IDX, CHORD_IDX = 0, 1, 2

# TODO: maybe implement transpositions on the encoded chords?
def transpose_chord_labels(chord_labels, s, mode="semitone"):
    """

    :param chord_labels:
    :param s:
    :param mode: can be either 'semitone' or 'fifth' and describes how transpositions are done.
    :return:
    """

    def shift_note(note):
        if note is None:
            logger.warning("Trying to shift a note that is None. Returning None")
            return None

        if note == "ambiguous":
            return "ambiguous"

        if mode == "semitone":
            # BEWARE: this never uses flats!
            note = find_enharmonic_equivalent(note)
            idx = (N2I[note.upper()] + s) % 12
            shifted_note = NOTES[idx] if note.isupper() else NOTES[idx].lower()
        elif mode == "fifth":
            idx = PF2I[note.upper()] + s
            if idx >= len(PITCH_FIFTHS):
                return None
            shifted_note = PITCH_FIFTHS[idx] if note.isupper() else PITCH_FIFTHS[idx].lower()
        else:
            raise ValueError('mode should be either "semitone" or "fifth"')
        return shifted_note

    transposed_chords = [
        Chord(shift_note(c.key), c.degree, c.quality, c.inversion, shift_note(c.root))
        for c in chord_labels
    ]
    return transposed_chords


def calculate_lr_transpositions_key(chords, spelling):
    """The number of transpositions can be negative if the original key is not allowed!"""
    assert spelling in ["pitch", "spelling"], "Please choose either pitch or spelling"
    if spelling == "pitch":
        return 6, 5
    keys = set([c.key for c in chords])
    nl, nr = 35, 35  # number of transpositions to the left or to the right
    for k in keys:
        i = PF2I[k.upper()]
        nl, nr = min(nl, i - KEY_START), min(nr, KEY_END - i)
    return nl, nr


def generate_chord_chunks(chords, chunk_size, hop_size, output_fpc):
    """Chords must be a list of Chord named tuples"""
    res = []
    elapsed = 0
    while elapsed + chunk_size * output_fpc < len(chords) + hop_size * output_fpc:
        chunk = chords[elapsed : elapsed + chunk_size * output_fpc]
        # Pad with repeating chords until the beginning of next crotchet
        while len(chunk) % output_fpc != 0:
            chunk.append(chunk[-1])
        elapsed += hop_size * output_fpc
        res.append(chunk)
    return res


def _load_chord_labels(chords_file, label_codec):
    """
    Load chords of each piece and add chord symbols into the labels.
    :param chords_file: the path to the file with the harmonic analysis
    :return: chord_labels, an array of tuples (start, end, key, degree, quality, inversion)
    """
    with open(chords_file, mode="r") as f:
        data = csv.reader(f)
        # The data columns are these: start, end, key, degree, quality, inversion
        if label_codec.use_ambiguous_label or label_codec.use_ambiguous_label_for_key_only:
            chords = [
                (
                    float(row[0]),
                    float(row[1]),
                    Chord(*row[2:-1], label_codec.find_chord_root_str(row[2], row[3])),
                    row[-1]
                )
                for row in data
            ]
        else:
            chords = [
                (
                    float(row[0]),
                    float(row[1]),
                    Chord(*row[2:], label_codec.find_chord_root_str(row[2], row[3])),
                )
                for row in data
            ]

    return chords


def _segment_chord_labels(chord_labels, score_duration, output_fpc=2):
    labels = []
    n_frames_to_backfill = 0
    for n in range(math.ceil(score_duration * output_fpc)):
        seg_time = n / output_fpc
        chords_found = [c[2] for c in chord_labels if c[0] <= seg_time < c[1]]
        if len(chords_found) == 0:
            logger.warning(f"Cannot read labels at frame {n}, time {seg_time}.")
            if labels:
                chords_found = [labels[-1]]
                logger.warning(f" Assuming that the previous chord is still valid: {chords_found}")
            else:
                n_frames_to_backfill += 1
                logger.warning(f" No valid chord found yet. Back-filling with the next one")
                continue

        if len(chords_found) > 1:
            logger.warning(
                f"More than one chord at frame {n} starting at crotchet {seg_time}:\n"
                f"{[l for l in chords_found]}. Using only the first one."
            )
        for _ in range(1 + n_frames_to_backfill):
            labels.append(chords_found[0])
        n_frames_to_backfill = 0
    return labels

def handle_ambiguity_in_chord_labels(chord_labels):
    modified_chord_labels = []
    for chord_label in chord_labels:
        if chord_label[-1] == "ambiguous":
            chord_label = (chord_label[ONSET_IDX], chord_label[OFFSET_IDX],
                           Chord("ambiguous",
                                 "ambiguous",
                                 chord_label[CHORD_IDX].quality,
                                 chord_label[CHORD_IDX].inversion,
                                 chord_label[CHORD_IDX].root))
        else:
            chord_label = (chord_label[ONSET_IDX], chord_label[OFFSET_IDX], chord_label[CHORD_IDX])
        modified_chord_labels.append(chord_label)

    return modified_chord_labels

def handle_ambiguity_in_chord_labels_for_key_only(chord_labels):
    modified_chord_labels = []
    for chord_label in chord_labels:
        if chord_label[-1] == "ambiguous":
            chord_label = (chord_label[ONSET_IDX], chord_label[OFFSET_IDX],
                           Chord("ambiguous",
                                 chord_label[CHORD_IDX].degree,
                                 chord_label[CHORD_IDX].quality,
                                 chord_label[CHORD_IDX].inversion,
                                 chord_label[CHORD_IDX].root))
        else:
            chord_label = (chord_label[ONSET_IDX], chord_label[OFFSET_IDX], chord_label[CHORD_IDX])
        modified_chord_labels.append(chord_label)

    return modified_chord_labels

def import_chords(chord_file, lc, output_fpc):
    chord_labels = _load_chord_labels(chord_file, lc)
    score_length = chord_labels[-1][1]

    if lc.use_ambiguous_label:
        chord_labels = handle_ambiguity_in_chord_labels(chord_labels)
    elif lc.use_ambiguous_label_for_key_only:
        chord_labels = handle_ambiguity_in_chord_labels_for_key_only(chord_labels)

    cl_segmented = _segment_chord_labels(chord_labels, score_length, output_fpc)
    return cl_segmented
