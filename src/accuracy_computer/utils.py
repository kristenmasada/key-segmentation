"""
"""

import os

import numpy as np

DO_NOT_EXCLUDE = 0

def get_filepaths_from_txt_file(txt_file_with_filepaths):
    """ Get list of filepaths from inside a .txt file.

    Parameters
    ----------
    txt_file_with_filepaths : str
    """
    with open(txt_file_with_filepaths) as txt_file:
        return txt_file.read().splitlines()

def strip_filename_from_filepath(filepath):
    """ Get name of file from filepath.

    Parameters
    ----------
    filepath : str
    """
    return os.path.splitext(os.path.basename(filepath))[0]

def exclude_events_outside_of_key_segments_from_event_key_labels(event_key_labels, key_segment_indices):
    """

    Parameters
    ----------
    event_key_labels : np.ndarray (dtype='int64', shape=(no. events,))
    key_segment_indices : np.ndarray (dtype='int64', shape=(no. key segments, 2))
    """
    event_key_labels_with_non_key_segment_events_removed = []
    for key_segment_idx in key_segment_indices:
        start_idx, stop_idx = key_segment_idx[0], key_segment_idx[1]

        if start_idx == stop_idx:
            continue

        event_key_labels_with_non_key_segment_events_removed.append(event_key_labels[start_idx:stop_idx])

    if len(event_key_labels_with_non_key_segment_events_removed) == 0:
        return np.asarray(event_key_labels_with_non_key_segment_events_removed)
    else:
        return np.concatenate(event_key_labels_with_non_key_segment_events_removed)

def exclude_specified_events_from_event_key_labels(event_key_labels, events_to_exclude):
    """

    Parameters
    ----------
    event_key_labels : 
    events_to_exclude :
    """
    event_key_labels_with_excluded_events_removed = []
    for event_idx, event in enumerate(events_to_exclude):
        if event == DO_NOT_EXCLUDE:
           event_key_labels_with_excluded_events_removed.append(event_key_labels[event_idx])

    return np.asarray(event_key_labels_with_excluded_events_removed)

def convert_key_indices_to_excluded_events_vector(key_segment_indices, num_events):
    """

    Parameters
    ----------
    key_segment_indices : np.ndarray (shape=(no. key segments, 2))
    num_events : int
    """
    excluded_events_vector = np.ones(num_events)

    for key_segment_idx in key_segment_indices:
        start_idx, stop_idx = key_segment_idx[0], key_segment_idx[1]
        excluded_events_vector[start_idx:stop_idx] = DO_NOT_EXCLUDE 

    return excluded_events_vector

def remove_songs_to_ignore_from_dict(songs_to_ignore, key_dict):
    """ Remove songs to ignore from inputted dictionary.

    Parameters
    ----------
    songs_to_ignore : list of str
    key_dict : dict of {str: np.ndarray}
    """
    for songname in songs_to_ignore:
        if songname in key_dict:
            key_dict.pop(songname)
    return key_dict

def truncate_song_event_key_probs_one_event_longer_than_ground_truth_labels(event_key_predictions, ground_truth_event_key_labels):
    """

    Parameters
    ----------
    event_key_predictions :
    ground_truth_event_key_labels :
    """
    num_song_events = event_key_predictions.shape[0]
    num_ground_truth_events = ground_truth_event_key_labels.shape[0]

    if num_song_events == (num_ground_truth_events + 1):
        event_key_predictions = event_key_predictions[:-1]
        num_song_events = event_key_predictions.shape[0]

    assert num_song_events == num_ground_truth_events

    return event_key_predictions

def compute_key_segment_length(key_segment):
    """

    Parameters
    ----------
    key_segment : 
    """
    return key_segment[-1] - key_segment[0]

def convert_one_hot_vector_events_to_event_key_labels(song_event_key_preds_dict):
    """

    Parameters
    ----------
    song_event_key_preds_dict : dict of {str: np.ndarray (dtype='float32', shape=(no. events, 24*))}
        *If `input_type` is 'pitch_bass'.
    """
    song_event_key_pred_labels_dict = {}
    for songname in song_event_key_preds_dict:
        song_event_key_pred_labels = compute_max_key_prediction_for_each_event_in_song(song_event_key_preds_dict[songname])
        song_event_key_pred_labels_dict[songname] = song_event_key_pred_labels

    return song_event_key_pred_labels_dict

def convert_event_key_probs_to_event_key_labels(song_event_key_probs_dict):
    """

    Parameters
    ----------
    song_event_key_probs_dict : dict of { : }
    """
    return convert_one_hot_vector_events_to_event_key_labels(song_event_key_probs_dict)

def compute_max_key_prediction_for_each_event_in_song(event_key_predictions_array):
    """

    Parameters
    ----------
    event_key_predictions_array :
    """
    return np.argmax(event_key_predictions_array, axis=1)

def get_consecutive_groups_of_indices(event_indices):
    """

    Parameters
    ----------
    event_indices : 

    Notes
    -----
    Below taken from https://stackoverflow.com/a/7353335
    """
    return np.split(event_indices, np.where(np.diff(event_indices) != 1)[0] + 1)

def get_key_segments_from_consecutive_idx_groups(song_key_pred_for_each_event, consecutive_idx_groups):
    """

    Parameters
    ----------
    song_key_pred_for_each_event : np.ndarray (shape=(no. events,), dtype='int64') 
    consecutive_idx_groups : list of np.ndarray

    Returns
    -------
    key_segments : list of [int, int] 
    """
    key_segments = []
    for idx_group in consecutive_idx_groups:
        key_segment_labels = song_key_pred_for_each_event[idx_group]

        key_segment_start_indices = [0]
        current_key_segment_label = key_segment_labels[0]
        for key_label_idx, key_label in enumerate(key_segment_labels[1:]):
            if key_label != current_key_segment_label:
                key_segment_start_indices.append(key_label_idx+1)
                current_key_segment_label = key_label

        for start_idx_num, key_segment_start_idx in enumerate(key_segment_start_indices):
            if start_idx_num == (len(key_segment_start_indices)-1):
                key_segment_idx = [idx_group[key_segment_start_idx], idx_group[-1]+1]
            else:
                next_key_segment_start_idx = key_segment_start_indices[start_idx_num+1]
                key_segment_idx = [idx_group[key_segment_start_idx], idx_group[next_key_segment_start_idx]]
            key_segments.append(key_segment_idx)

    return key_segments 